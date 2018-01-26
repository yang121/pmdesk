#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import pymongo
import re
from random import choice

import redis

from pmdesk.settings import MAX_SCORE, MIN_SCORE, INITIAL_SCORE
from pmdesk.settings import REDIS_HOST, REDIS_PORT, REDIS_PASSWORD, REDIS_KEY
from proxypool.error import PoolEmptyError


class RedisHandler(object):
    def __init__(self, host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD):
        """
        初始化
        :param host: Redis 地址
        :param port: Redis 端口
        :param password: Redis密码
        """
        self.db = redis.StrictRedis(host=host, port=port, password=password, decode_responses=True)

    def add(self, proxy, score=INITIAL_SCORE):
        """
        添加代理，设置分数为最高
        :param proxy: 代理
        :param score: 分数
        :return: 添加结果
        """
        if not re.match('\d+\.\d+\.\d+\.\d+\:\d+', proxy):
            print('代理不符合规范', proxy, '丢弃')
            return
        if not self.db.zscore(REDIS_KEY, proxy):
            return self.db.zadd(REDIS_KEY, score, proxy)

    def random(self):
        """
        随机获取有效代理，首先尝试获取最高分数代理，如果不存在，按照排名获取，否则异常
        :return: 随机代理
        """
        result = self.db.zrangebyscore(REDIS_KEY, MAX_SCORE, MAX_SCORE)
        if len(result):
            return choice(result)
        else:
            result = self.db.zrevrange(REDIS_KEY, 0, 100)
            if len(result):
                return choice(result)
            else:
                raise PoolEmptyError

    def decrease(self, proxy):
        """
        代理值减一分，小于最小值则删除
        :param proxy: 代理
        :return: 修改后的代理分数
        """
        score = self.db.zscore(REDIS_KEY, proxy)
        if score and score > MIN_SCORE:
            print('代理', proxy, '当前分数', score, '减1')
            return self.db.zincrby(REDIS_KEY, proxy, -1)
        else:
            print('代理', proxy, '当前分数', score, '移除')
            return self.db.zrem(REDIS_KEY, proxy)

    def exists(self, proxy):
        """
        判断是否存在
        :param proxy: 代理
        :return: 是否存在
        """
        return not self.db.zscore(REDIS_KEY, proxy) == None

    def max(self, proxy):
        """
        将代理设置为MAX_SCORE
        :param proxy: 代理
        :return: 设置结果
        """
        print('代理', proxy, '可用，设置为', MAX_SCORE)
        return self.db.zadd(REDIS_KEY, MAX_SCORE, proxy)

    def count(self):
        """
        获取数量
        :return: 数量
        """
        return self.db.zcard(REDIS_KEY)

    def all(self):
        """
        获取全部代理
        :return: 全部代理列表
        """
        return self.db.zrangebyscore(REDIS_KEY, MIN_SCORE, MAX_SCORE)

    def batch(self, start, stop):
        """
        批量获取
        :param start: 开始索引
        :param stop: 结束索引
        :return: 代理列表
        """
        return self.db.zrevrange(REDIS_KEY, start, stop - 1)


class MongoDBHandler(object):

    def __init__(self, mongo_url, mongo_db, mongo_table):
        self.client = pymongo.MongoClient(mongo_url, connect=False)
        self.db = self.client[mongo_db]
        self.table = self.db[mongo_table]

    def close(self):
        self.client.close()

    def or_filter(self, condition, show_id=0):
        """
        or查找
        :param condition: [{'k':'v1'},{'k':'v2'},]
        :param show_id: 1 or 0
        :return: list for dictionary
        """
        return list(self.table.find({'$or': condition}, {"_id": show_id}))

    def and_filter(self, condition, show_id=0):
        """
        and查找
        :param condition: {'k1':'v1','k2':'v2'},
        :param show_id: 1 or 0
        :return: list for dictionary
        """
        return list(self.table.find(condition, {"_id": show_id}))

    def insert_many(self, data):
        """
        批量插入
        :param data: list for dictionary
        :return:
        """
        return self.table.insert_many(data)

    def update(self, condition, field):
        """
        更新特定内容的字段
        :param condition: dictionary for filter field
        :param field: dictionary for field to be updated
        :return:
        """
        return self.table.update(condition, {"$set":field})