#!/usr/bin/env python3
# -*- coding:utf-8 -*-

VALID_STATUS_CODES = [200,]

DEBUG = False
PAGE_RANGE = 501, 510

MONGO_URL = 'localhost'
MONGO_DB = 'papa'
MONGO_TABLE = 'app_name'

PROXY_MODE = True
PROXY_GET_URL = 'http://0.0.0.0:5555/random'