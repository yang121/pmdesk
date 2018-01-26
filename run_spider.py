#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import sys


from pmdesk.settings import *
sys.path.append(BASEDIR)
from spider.appname import run



if __name__ == '__main__':
    run()