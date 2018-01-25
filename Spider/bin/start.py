#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import os, sys
from multiprocessing.pool import Pool
from time import sleep

BASEDIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# SURBASEDIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASEDIR)
# sys.path.append(SURBASEDIR)

from Spider.appname_spider import main as catch_appname
from ProxyPool.run import main as proxy

if __name__ == '__main__':
    pool = Pool()
    p1 = pool.Process(target=proxy)
    p1.start()
    p2 = pool.Process(target=catch_appname)
    print('10秒后开始抓app名')
    sleep(10)
    p2.start()
    Pool.close(pool)