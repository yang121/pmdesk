#!/usr/bin/env python3
# -*- coding:utf-8 -*-


from pmdesk.settings import *
sys.path.append(BASEDIR)
from spider.appname_spider import run

if __name__ == '__main__':
    run()