#!/usr/bin/env python3
# -*- coding:utf-8 -*-


import requests
from requests import RequestException
from pyquery.pyquery import PyQuery as pq
import config
from dbhandler import MongoDBHandler


def get_page_index(n, DEBUG=False):

    try:
        url = 'http://shouji.baidu.com/software/%s/' % n
        response = requests.get(url)
        if response.status_code == 200:
            cn_page = response.content.decode('utf-8')
            doc = pq(cn_page)
            page_num = int(doc('.next').prev('li').children().text())
            print('total page: ', page_num)
            if DEBUG:
                page_num = 2
            for pn in range(1, page_num):
                sub_url = 'http://shouji.baidu.com/software/%s/list_%s.html' % (n, pn)
                print()
                print('====================================================')
                print('正在爬: ', sub_url)
                sub_response = requests.get(sub_url)
                if sub_response.status_code == 200:
                    yield sub_response.content.decode('utf-8')
                else:
                    raise RequestException
        else:
            raise RequestException
    except RequestException as e:
        print('网络错误！', e)


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


def main():
    if config.DEBUG:
        page_range = 501, 502
    else:
        page_range = config.PAGE_RANGE

    print(page_range)

    for n in range(*page_range):
        htmls = get_page_index(n, config.DEBUG)
        for html in htmls:
            items = parse_page_index(html)
            if items:
                conn = MongoDBHandler(config.MONGO_URL, config.MONGO_DB, config.MONGO_TABLE)
                conn.save_to_app_name(items)


if __name__ == '__main__':
    main()
    print('完成！')