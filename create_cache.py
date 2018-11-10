#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     createChache.py
   Description :    生成缓存
   Author :       david
   date：          2018/6/15
-------------------------------------------------
   Change Activity:
                   2018/6/15:
-------------------------------------------------
"""
import requests
import os
import json
from dotenv import load_dotenv, find_dotenv

# 加载配置文件
load_dotenv(find_dotenv())
CACHE_USER = os.getenv('CACHE_USER')
CACHE_PASS = os.getenv('CACHE_PASS')

url = os.getenv('CREATE_CACHE_URL')


def create_cache(key, value, exit=60 * 60 * 24):
    data = {u'key': key, u'value': value, 'exit': exit}
    response = requests.post(url, json=data)
    return response.json()


if __name__ == '__main__':
    dataInfo = {'pageNo': 5, 'pagesize': 20}
    result = create_cache('aaa', dataInfo)
    print(result)
