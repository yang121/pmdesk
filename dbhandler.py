#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import pymongo
from copy import deepcopy


class MongoDBHandler(object):

    def __init__(self, mongo_url, mongo_db, mongo_talbe):
        self.client = pymongo.MongoClient(mongo_url, connect=False)
        self.db = self.client[mongo_db]
        self.table = self.db[mongo_talbe]

    def save_to_app_name(self, items):
        data = list(items)
        filter_word = [{'apk_name':i.pop('apk_name')} for i in deepcopy(data)]

        exist_data = list(self.table.find({'$or': filter_word}, {"_id": 0}))
        if exist_data == data:
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
                print('新增', d)


            if update_list:
                for u in update_list:
                    akp_name = u['apk_name']
                    name = u['name']
                    if self.table.update({'apk_name': akp_name}, {"$set":{'name': name}}):
                        print('%s应用名更新为%s' % (akp_name, name))
        if insert_list:
            res = self.table.insert_many(insert_list)
            if res.acknowledged:
                print('本次共新增%s条数据' % len(res.inserted_ids))
        try:
            print('更新%s条数据' % len(update_list))
        except:
            pass