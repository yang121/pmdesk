#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from multiprocessing.pool import Pool

import requests
from pyquery.pyquery import PyQuery as pq
from requests import RequestException

from pmdesk import settings
from repository.dbhandler import MongoDBHandler, RedisHandler


# from ProxyPool.proxypool.repository import RedisClient

def get_html(url, proxies=None):

    while True:
        if proxies:
            proxies = {'http': get_proxy()}
        try:
            response = requests.get(url, proxies=proxies, timeout=2)
            if response.status_code in settings.VALID_STATUS_CODES:
                data = response.content.decode('utf-8')
                if data:
                    response.close()
                    return data

        except RequestException as e:
            print('读取%s失败！正在更换代理...' % url, e)
            redis = RedisHandler()
            redis.decrease(url)



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


def get_proxy():
    while True:
        r = requests.get(settings.PROXY_GET_URL)
        # proxy = BeautifulSoup(r.text, "lxml").get_text()
        proxy = r.text
        if proxy:
            print('正在使用代理', proxy)
            return proxy

def main(n):
    """
    所有环节串联
    :param n:
    :return:
    """
    htmls = get_page_index(n, DEBUG=settings.DEBUG)
    for html in htmls:
        items = parse_page_index(html)
        if items:
            conn = MongoDBHandler(settings.MONGO_URL, settings.MONGO_DB, settings.MONGO_TABLE)
            try:
                conn.save_to_app_name(items)
            except Exception as e:
                print('服务器储存发生错误:',  e)
            finally:
                conn.close()
    print('%s页完成！' % n)


def run():
    if settings.DEBUG:
        page_range = 501, 502
    else:
        page_range = settings.PAGE_RANGE

    print(page_range)

    print([n for n in range(*page_range)])

    for n in range(*page_range):
        main(n)

    pool = Pool()
    pool.map(main, [n for n in range(*page_range)])

if __name__ == '__main__':
    run()