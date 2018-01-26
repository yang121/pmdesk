#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import pymongo
from copy import deepcopy


class MongoDBHandler(object):

    def __init__(self, mongo_url, mongo_db, mongo_table, *args, **kwargs):
        """
        :param mongo_url: 数据库url
        :param mongo_db: 数据库名
        :param mongo_table: 数据库表名
        :param args:
        :param kwargs:
        """
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
        return self.table.update(condition, {"$set": field})


class APPNameMongoDBHandler(MongoDBHandler):
    def __init__(self, mongo_url, mongo_db, mongo_table, *args, **kwargs):
        super().__init__(mongo_url, mongo_db, mongo_table, *args, **kwargs)

    def save_to_table(self, key_field, items):
        """
        将app的name和apk_name存入mongoDB，有则更新或跳过，无则新增。
        :param key_field: 主键、索引或其他用作识别的字段名称，检查数据是否存在
        :param items: 序列 or 生成器
        :return:
        """
        data = []
        for i in items:
            data.append(i)

        condition = [{key_field: i.pop(key_field)} for i in deepcopy(data)]
        if not condition:
            print('此数据中不含%s，丢弃：' % key_field, data)
            return

        exist_data = self.or_filter(condition)
        if exist_data == data:
            print('无需更新')
            self.close()
            return

        insert_list = deepcopy(data)
        if exist_data:
            update_list = []
            exist_apk_name = [ed[key_field] for ed in exist_data]

            for d in data:
                if d in exist_data:
                    insert_list.remove(d)
                    continue
                if d[key_field] in exist_apk_name:
                    update_list.append(d)
                    insert_list.remove(d)
                    continue

            if update_list:
                # for u in update_list:
                #     akp_name = u[key_field]
                #     name = u['name']
                #     if self.update({key_field: akp_name}, {"$set": {'name': name}}):
                #         print('%s应用名更新为%s' % (akp_name, name))
                for u in update_list:
                    key_field_value = u.pop(key_field)
                    if self.update({key_field: key_field_value}, {"$set": u}) and print(u):
                        print('%s更新为%s' % (key_field_value, u))

            print('更新%s条数据' % len(update_list))

        if insert_list:
            res = self.insert_many(insert_list)
            print('保存状态：', res.acknowledged)
            if res.acknowledged:
                print('新增%s条数据' % len(res.inserted_ids))

        self.close()
