#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import pymongo
from copy import deepcopy
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

    def __init__(self, mongo_url, mongo_db, mongo_talbe):
        self.client = pymongo.MongoClient(mongo_url, connect=False)
        self.db = self.client[mongo_db]
        self.table = self.db[mongo_talbe]

    def close(self):
        self.client.close()

    def save_to_app_name(self, items):
        """
        将app的name和apk_name存入mongoDB
        :param items: 序列及生成器
        :return:
        """
        data = list(items)
        filter_word = [{'apk_name': i.pop('apk_name')} for i in deepcopy(data)]

        exist_data = list(self.table.find({'$or': filter_word}, {"_id": 0}))
        if exist_data == data:
            print('无需更新')
            return
        insert_list = deepcopy(data)
        if exist_data:
            # """
            # [
            #     {'name': 'name1','apk_name': 'apkname1'},
            #     {'name': 'name2','apk_name': 'apkname2'},
            #     {'name': 'name3','apk_name': 'apkname3'},
            # ]
            #
            # """

            update_list = []
            exist_apk_name = [ed['apk_name'] for ed in exist_data]

            for d in data:
                if d in exist_data:
                    insert_list.remove(d)
                    continue
                if d['apk_name'] in exist_apk_name:
                    # print(d['apk_name'], '更新应用名为', d['name'])
                    update_list.append(d)
                    insert_list.remove(d)
                    continue


            if update_list:
                for u in update_list:
                    akp_name = u['apk_name']
                    name = u['name']
                    if self.table.update({'apk_name': akp_name}, {"$set":{'name': name}}):
                        print('%s应用名更新为%s' % (akp_name, name))

            print('更新%s条数据' % len(update_list))

        if insert_list:
            res = self.table.insert_many(insert_list)
            print('保存状态：', res.acknowledged)
            if res.acknowledged:
                print('新增%s条数据' % len(res.inserted_ids))