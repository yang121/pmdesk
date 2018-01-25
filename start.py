#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from multiprocessing.pool import Pool
from time import sleep
from pmdesk.settings import *

sys.path.append(BASEDIR)

from spider.appname_spider import run as catch_appname
from run_proxy_pool import main as proxy

if __name__ == '__main__':
    pool = Pool()
    p1 = pool.Process(target=proxy)
    p1.start()
    p2 = pool.Process(target=catch_appname)
    print('10秒后开始抓app名')
    sleep(10)
    p2.start()
    Pool.close(pool)