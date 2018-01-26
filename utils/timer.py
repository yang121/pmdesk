#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import time


def timer(func):
    def wrap(*args, **kwargs):
        start = time.time()
        res = func(*args, **kwargs)
        end = time.time()
        print('全部完成，耗时%s分钟'% int((int(end - start)/60)))
        return res
    return wrap