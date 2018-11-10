#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     alimama-pid.py
   Description :    批量添加PID
   Author :       david
   date：          2018/11/6
-------------------------------------------------
   Change Activity:
                   2018/11/6:
-------------------------------------------------
"""
from dotenv import load_dotenv, find_dotenv
import os

import pymysql

# 加载配置文件
load_dotenv(find_dotenv())
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')

from sqlalchemy import create_engine  # 引入sqlalchemy   #引擎
import datetime
import json
import time
import random
import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import pandas as pd
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


class Order(object):
    def __init__(self):
        self.web = webdriver.Chrome()
        # 选品库数量
        self.selection_count = 0
        self.headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.8,en;q=0.6',
            'cache-control': 'max-age=0',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.78 Safari/537.36'
        }
        self.req = requests.Session()
        self.cookies = {}

    def login(self):
        self.web.get(
            'https://login.taobao.com/member/login.jhtml?style=mini&newMini2=true&css_style=alimama&from=alimama&redirectURL=http%3A%2F%2Fwww.alimama.com&full_redirect=true&disableQuickLogin=true')

        i = input('请确认是否已登录？[y/n]:')
        if (i != 'y'):
            return

        self.web.get('https://pub.alimama.com/promo/search/index.htm')
        time.sleep(4)
        cookie = ''
        for elem in self.web.get_cookies():
            cookie += elem["name"] + "=" + elem["value"] + ";"
            if elem["name"] == '_tb_token_':
                self.token = elem["value"]
        self.cookies = cookie
        self.headers['Cookie'] = self.cookies
        # self.web.quit()

    def create_pid(self, gcid, siteid, taobaoId, name, start=0, end=5000):
        clickButton = self.web.find_element_by_xpath(
            "//div[@class='search-result-wrap search-result-wrap-block clearfix']/div[2]/div[@class='box-btn-group']/a[@class='box-btn-left']")
        self.web.execute_script("arguments[0].scrollIntoView();", clickButton)  # 移动到视窗范围内
        clickButton.click()  # 点击立即推广
        time.sleep(5)

        while end > start:

            print(name + str(start))
            res = self.req.post('http://pub.alimama.com/common/adzone/selfAdzoneCreate.json', data={
                'tag': '29',
                'gcid': gcid,
                'siteid': siteid,  # 这里改成导购位ID
                'selectact': 'add',
                'newadzonename': name + str(start),
                '_tb_token_': self.token
            }, headers=self.headers)

            # print(res.json())

            result = res.json()

            if result['ok']:

                adzoneid = result['data']['adzoneId']
                pid = "mm_%s_%s_%s" % (taobaoId, siteid, adzoneid)

                # 打开数据库连接
                db = pymysql.connect(DB_HOST, DB_USER, DB_PASSWORD, DB_NAME, charset="utf8")

                # 使用cursor()方法获取操作游标
                cursor = db.cursor()

                # 生成SQL
                created_at = updated_at = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                sql = "INSERT taobaoPid (pid, name, siteId, adzoneId,  taobaoId, created_at, updated_at)" \
                      " VALUE (%s, %s, %s, %s, %s, %s, %s);"
                # sql = "INSERT INTO taobaoPid (`pid`, `name`, `siteId`, `adzoneId`,  `taobaoId`, `created_at`, `updated_at`) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                # print(sql)
                # 执行sql语句
                # cursor.execute(sql,['mm_133273614_45854565_55174500297', '指彩1', '45854565', '55174500297', '133273614', '2018-11-7 19:04:42', '2018-11-7 19:04:42'])
                cursor.execute(sql,[pid, name + str(start), siteid, adzoneid, taobaoId, created_at, updated_at])
                # 执行sql语句
                db.commit()
                # 关闭数据库连接
                db.close()

                start = start + 1
                time.sleep(random.randint(3, 10))
                # 循环结束
            else:
                print('创建失败', result)
                break


if __name__ == '__main__':
    try:
        order = Order()
        order.login()
        order.create_pid(gcid='0', siteid='45854565', taobaoId='133273614', name='指彩', start=4982, end=5000)

        order.web.close()
    except Exception as e:
        print('出错了',e)
    pass
