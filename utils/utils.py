from time import sleep

import requests
from requests import RequestException

from repository.dbhandler import RedisHandler
from pmdesk import settings


# def get_page(url, options={}):
#     """
#     抓取代理
#     :param url:
#     :param options:
#     :return:
#     """
#     headers = dict(base_headers, **options)
#     print('正在抓取', url)
#     try:
#         response = requests.get(url, headers=headers)
#         print('抓取成功', url, response.status_code)
#         if response.status_code == 200:
#             return response.text
#     except ConnectionError:
#         print('抓取失败', url)
#         return None


def get_page(url, proxies=False, options={}, vaild_code=(200,)):
    headers = dict(settings.BASE_HEADERS, **options)

    while True:
        if proxies:
            proxies = {'http': get_proxy()}
        try:
            response = requests.get(url, proxies=proxies,
                                    headers=headers,  # 处理完当前事务后关闭连接
                                    timeout=5)
            if response.status_code in vaild_code:
                data = response.content.decode('utf-8')
                if data:
                    print('抓取成功', response.status_code)
                    response.close()
                    return data
        except RequestException as e:
            print('连接%s失败！正在更换代理...' % url, e)
            redis = RedisHandler()
            redis.decrease(url)


def get_proxy():
    while True:
        r = requests.get(settings.PROXY_GET_URL)
        proxy = r.text
        if proxy:
            print('正在使用代理', proxy)
            return proxy