#! /usr/bin/env python3
# -*- coding: utf-8 -*-

'''产品分类数据抓取'''

from dotenv import load_dotenv,find_dotenv
import os
import requests
import pymysql
import time

#加载配置文件
load_dotenv(find_dotenv())
DB_HOST= os.getenv('DB_HOST')
DB_PORT=os.getenv('DB_PORT')
DB_USER=os.getenv('DB_USER')
DB_PASSWORD=os.getenv('DB_PASSWORD')
DB_NAME=os.getenv('DB_NAME')

# 省钱快报
r = requests.get('http://api.17gwx.com/operate/discover?app_installtime=1527633664&app_version=2.6.8&channel_name=AppStore&client_id=2&device_id=4E6F2D54-35DB-43E0-B3AF-4E482F257B1A&device_info=iPhone9%2C2&gender=0&idfa=3A7B4D0A-1C9B-4377-8AF3-36F6B5FA18BC&network=Wifi&os_version=10.3.3&sign=0d77a9c9b6d17912bc13795f75eda947&timestamp=1528771950')

rJson = r.json()
res = rJson['data']['zhekou_discover_left_nav']
categories = []
for x in res:
    v = {}
    v['id'] = x['element_id']
    v['parent_id'] = x['parent_element']
    v['title'] = x['title']
    categories.append(v)
    for y in x['children']['webview']:
         v ={}
         v['id'] = y['element_id']
         v['parent_id'] = y['parent_element']
         v['title'] = y['title']
         categories.append(v)
         # img = requests.get(y['pic'])
         # # imgName = 'img/category/' + y['title'].replace('/','') + str(y['element_id']) + '.jpg'
         # imgName = 'category/' + str(y['element_id']) + '.jpg'
         # with open(imgName, 'ab') as f:
         #     f.write(img.content)
         #     f.close()
         # print(imgName)

# 打开数据库连接
db = pymysql.connect(DB_HOST,DB_USER,DB_PASSWORD,DB_NAME,charset="utf8" )

# 使用cursor()方法获取操作游标
cursor = db.cursor()

t = time.time()

try:
    for category in categories:
        if category['parent_id'] == 0:
            base_url = ''
            img_path = ''
        else:
            base_url = 'http://zg-storage.zhicaikeji.com/source'
            img_path = 'category/' + str(category['id']) + '.jpg'
        # SQL 插入语句
        sql = "INSERT INTO zg_goods_category(`id` ,  `parent_id` ,  `title` ,`status`,`img_path`,`img_base_url`,\
        `created_at`, `updated_at`, `created_by`, `updated_by`) VALUES('%d', '%d', '%s',1,'%s','%s', '%d', '%d', 1,1)\
        " %  (category['id'], category['parent_id'], category['title'], img_path ,base_url, int(t),int(t))
        print(sql)
        #执行sql语句
        # cursor.execute(sql)
    # 执行sql语句
    db.commit()
except Exception as e:
    print('发生异常：',e)
    # 发生错误时回滚
    db.rollback()

# 关闭数据库连接
db.close()