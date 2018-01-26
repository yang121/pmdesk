#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import pymongo


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
        return self.table.update(condition, {"$set": field})