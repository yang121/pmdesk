from time import sleep

import requests
from requests import RequestException
from pyquery.pyquery import PyQuery as pq

from repository.RedisHandler import ProxyRedisHandler
from pmdesk import settings


def get_page(url, proxies=None, options={}, valid_code=(200,), selector=None):
    headers = dict(settings.BASE_HEADERS, **options)

    while True:
        if proxies:
            proxies = get_proxy()
        try:
            response = requests.get(url, proxies={'http': proxies},
                                    headers=headers,  # 处理完当前事务后关闭连接
                                    timeout=settings.TIME_OUT)
            if response.status_code in valid_code:
                try:
                    data = response.content.decode('utf-8')
                except UnicodeDecodeError:
                    data = response.text
                if data:
                    print('抓取成功', response.status_code)
                    response.close()
                    if selector:
                        doc = pq(data)
                        if doc(selector):
                            return data
                        else:
                            continue
                    return data
        except RequestException as e:
            if proxies:
                print('连接%s失败！正在更换代理...' % url, e)
                sleep(5)
                redis = ProxyRedisHandler()
                redis.decrease(proxies)
            else:
                print('无法连接到,10秒后再试：', url)
                sleep(10)


def get_proxy():
    while True:
        r = requests.get(settings.PROXY_GET_URL)
        proxy = r.text
        if proxy:
            print('正在使用代理', proxy)
            return proxy