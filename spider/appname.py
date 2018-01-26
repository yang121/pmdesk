#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from multiprocessing.pool import Pool

from copy import deepcopy
from pyquery.pyquery import PyQuery as pq

from pmdesk import settings
from repository.dbhandler import MongoDBHandler
from utils.utils import get_page


def crawl_baidu_shouji(n, proxies=True, debug=False):
    """
    根据分类首页获得最大页码决定范围，暂时只适配百度url
    :param n:
    :param proxies:
    :param debug:
    :return:
    """
    url = 'http://shouji.baidu.com/software/%s/' % n
    while True:
        html = get_page(url, proxies, vaild_code=settings.VALID_STATUS_CODES)
        doc = pq(html)
        try:
            page_num = int(doc('.next').prev('li').children().text())
        except ValueError as e:
            print('获取信息失败: ', e)
            continue

        print('total page: ', page_num)
        if debug:
            page_num = 2
        for pn in range(1, page_num + 1):
            sub_url = 'http://shouji.baidu.com/software/%s/list_%s.html' % (n, pn)
            print()
            print('==============================================================')
            print('正在爬: ', sub_url)
            yield get_page(sub_url, proxies)
        break


def parse_page_index(html):
    sub_doc = pq(html)
    down_btn = sub_doc('div.app-detail > p.down-btn > span')
    if down_btn:
        print('本页有%s个应用' % down_btn.length)
        for d in down_btn.items():
            name = d.attr('data_name').strip()
            apk_name = d.attr('data_package').strip()
            data = {
                'name': name,
                'apk_name': apk_name
            }
            yield data
    else:
        print('无数据！')


def save_to_app_name(items):
    """
    将app的name和apk_name存入mongoDB
    :param items: 序列 or 生成器
    :return:
    """
    data = list(items)
    condition = [{'apk_name': i.pop('apk_name')} for i in deepcopy(data)]
    if condition:
        print('此数据中不含包名，丢弃：', items)
        return

    mongo = MongoDBHandler(settings.MONGO_URL, settings.MONGO_DB, 'apk_name')
    exist_data = mongo.or_filter(condition)
    if exist_data == data:
        print('无需更新')
        mongo.close()
        return

    insert_list = deepcopy(data)
    if exist_data:
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
                if mongo.update({'apk_name': akp_name}, {"$set": {'name': name}}):
                    print('%s应用名更新为%s' % (akp_name, name))

        print('更新%s条数据' % len(update_list))

    if insert_list:
        res = mongo.insert_many(insert_list)
        print('保存状态：', res.acknowledged)
        if res.acknowledged:
            print('新增%s条数据' % len(res.inserted_ids))

    mongo.close()


def main(n):
    """
    所有环节串联
    :param n:
    :return:
    """
    htmls = crawl_baidu_shouji(n, proxies=settings.PROXY_MODE, debug=settings.DEBUG)
    for html in htmls:
        items = parse_page_index(html)
        if items:
            try:
                save_to_app_name(items)
            except Exception as e:
                print('MongoDB错误:', items, '被忽略', e)
    print('%s页完成！' % n)


def run():
    if settings.DEBUG:
        page_range = 501, 502
    else:
        page_range = settings.PAGE_RANGE

    pool = Pool()
    pool.map(main, [n for n in range(*page_range)])


if __name__ == '__main__':
    run()