#!/usr/bin/env python3
# -*- coding:utf-8 -*-


from multiprocessing.pool import Pool

from pyquery.pyquery import PyQuery as pq

from pmdesk import settings
from repository.MongoDBHandler import APPNameMongoDBHandler
from utils.spider_utils import get_page
from utils.timer import timer


def crawl_chandashi_ios(keyword, proxies=True, debug=False):
    """
    根据分类首页获得最大页码决定范围，暂时只适配百度url
    :param n:
    :param proxies:
    :param debug:
    :return:
    """
    base_url = 'https://www.chandashi.com'
    url = base_url + '/search/index.html?keyword=%s&type=store' % keyword
    while True:
        html = get_page(url, proxies, selector='#searchlist')
        doc = pq(html)
        try:
            ios_url = base_url + doc('#searchlist > div:nth-child(1) > div > a').attr('href')
            ios_html = get_page(ios_url, proxies)
            print('==============================================================')
            print('正在爬: ', ios_url)
            ios_doc = pq(ios_html)
            android_url = base_url + ios_doc(
                '#pageTop > header > nav.navbar.nav-an.mobile-hide > div > div > ul > li:nth-child(2) > a'
            ).attr('href')
            android_html = get_page(android_url, proxies)

            yield ios_html, android_html

        except Exception as e:
            print('获取信息失败: ', e)
            continue

#
# def parse_baidu_shouji(html):
#     doc = pq(html)
#     down_btn = doc('p.down-btn > span')
#     if down_btn:
#         print('本页有%s个应用' % down_btn.length)
#         for d in down_btn.items():
#             name = d.attr('data_name').strip()
#             apk_name = d.attr('data_package').strip()
#             if name and apk_name:
#                 data = {
#                     'name': name,
#                     'apk_name': apk_name
#                 }
#                 yield data
#     else:
#         print('无数据！')
#
#
# def main(n):
#     """
#     所有环节串联
#     :param n:
#     :return:
#     """
#     htmls = crawl_baidu_shouji(n, proxies=settings.PROXY_MODE, debug=settings.DEBUG)
#     for html in htmls:
#         items = parse_baidu_shouji(html)
#         try:
#             mongo = APPNameMongoDBHandler(settings.MONGO_URL, settings.MONGO_DB, 'app_name')
#             mongo.save_to_table('apk_name', items)
#         except Exception as e:
#             print('MongoDB错误:', list(items), '被忽略', e)
#     print('%s页抓取完成！' % n)
#
#
# @timer
# def run():
#     if settings.DEBUG:
#         page_range = 501, 502
#     else:
#         page_range = settings.PAGE_RANGE
#
#     pool = Pool()
#     pool.map(main, [n for n in range(*page_range)])
#
#
# if __name__ == '__main__':
#     run()