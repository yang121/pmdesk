#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from multiprocessing.pool import Pool
from time import sleep

import requests
from pyquery.pyquery import PyQuery as pq
from requests import RequestException

from Spider.conf import config
from db.dbhandler import MongoDBHandler
# from ProxyPool.proxypool.db import RedisClient

def get_html(url, proxies=None):
    if proxies:
        proxies = {'http': get_proxy()}
    while True:
        try:
            response = requests.get(url, proxies=proxies, timeout=2)
            if response.status_code in config.VALID_STATUS_CODES:
                data = response.content.decode('utf-8')
                if data:
                    response.close()
                    return data

        except RequestException as e:
            print('读取%s失败！正在更换代理...' % url, e)


def get_page_index(n, proxies=True, DEBUG=False):
    """
    根据分类首页获得最大页码决定范围，暂时只适配百度url
    :param n:
    :param DEBUG:
    :return:
    """
    url = 'http://shouji.baidu.com/software/%s/' % n
    while True:
        html = get_html(url, proxies)
        doc = pq(html)
        try:
            page_num = int(doc('.next').prev('li').children().text())
        except ValueError as e:
            print('获取信息失败: ', e)
            continue

        print('total page: ', page_num)
        if DEBUG:
            page_num = 2
        for pn in range(1, page_num + 1):
            sub_url = 'http://shouji.baidu.com/software/%s/list_%s.html' % (n, pn)
            print()
            print('==============================================================')
            print('正在爬: ', sub_url)
            yield get_html(sub_url)
    #
    # while flag:
    #     try:
    #         if proxies_func:
    #             proxies = {'http': proxies_func()}
    #         else:
    #             proxies = None
    #         response = requests.get(url, proxies=proxies, timeout=2)
    #         if response.status_code in config.VALID_STATUS_CODES:
    #             cn_page = response.content.decode('utf-8')
    #             doc = pq(cn_page)
    #             page_num = int(doc('.next').prev('li').children().text())
    #             response.close()
    #             print('total page: ', page_num)
    #             if DEBUG:
    #                 page_num = 2
    #             for pn in range(1, page_num + 1):
    #                 sub_url = 'http://shouji.baidu.com/software/%s/list_%s.html' % (n, pn)
    #                 print()
    #                 print('==============================================================')
    #                 print('正在爬: ', sub_url)
    #                 flag = True
    #                 while flag:
    #                     try:
    #                         sub_response = requests.get(sub_url, proxies=proxies, timeout=2)
    #                         if sub_response.status_code == 200:
    #                             yield sub_response.content.decode('utf-8')
    #                             flag = False
    #                         else:
    #                             print(sub_response.status_code)
    #
    #                         sub_response.close()
    #                     except RequestException as e:
    #                         print('读取%s失败！正在更换代理...' % sub_url, e)
    #                     if proxies_func:
    #                         proxies = {'http': proxies_func()}
    #                     else:
    #                         proxies = None
    #
    #     except RequestException as e:
    #         print('读取%s失败！正在更换代理...' %  url, e)
    #
    #     except ValueError as e:
    #         print('获取信息失败: ',e)


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


def get_proxy():
    while True:
        r = requests.get(config.PROXY_GET_URL)
        # proxy = BeautifulSoup(r.text, "lxml").get_text()
        proxy = r.text
        if proxy:
            print('正在使用代理', proxy)
            return proxy

def main(n):

    htmls = get_page_index(n, DEBUG=config.DEBUG)
    for html in htmls:
        items = parse_page_index(html)
        if items:
            conn = MongoDBHandler(config.MONGO_URL, config.MONGO_DB, config.MONGO_TABLE)
            try:
                conn.save_to_app_name(items)
            except Exception as e:
                print('服务器储存发生错误:',  e)
            finally:
                conn.close()
    print('完成！')


if __name__ == '__main__':
    if config.DEBUG:
        page_range = 501, 502
    else:
        page_range = config.PAGE_RANGE

    print(page_range)

    pool = Pool()
    pool.map(main, [n for n in range(*page_range)])