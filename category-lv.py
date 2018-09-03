#! /usr/bin/env python3
# -*- coding: utf-8 -*-

'''产品分类数据抓取 针对lavarel'''

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
DB_NAME='hst-lv' #os.getenv('DB_NAME')

# 省钱快报
r = requests.get('http://api.17gwx.com/operate/discover?app_installtime=1527633664&app_version=2.6.8&channel_name=AppStore&client_id=2&device_id=4E6F2D54-35DB-43E0-B3AF-4E482F257B1A&device_info=iPhone9%2C2&gender=0&idfa=3A7B4D0A-1C9B-4377-8AF3-36F6B5FA18BC&network=Wifi&os_version=10.3.3&sign=0d77a9c9b6d17912bc13795f75eda947&timestamp=1528771950')

rJson = r.json()
res = rJson['data']['zhekou_discover_left_nav']
categories = []
# 打开数据库连接
db = pymysql.connect(DB_HOST,DB_USER,DB_PASSWORD,DB_NAME,charset="utf8" )

# 使用cursor()方法获取操作游标
cursor = db.cursor()
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
         change_category = {
             '韩版潮包':'日韩潮包',
             '电饭锅/煲':'电饭锅',
             '纸尿裤':'尿布湿',
             '糖巧奶酪':'糖果奶酪',
             '雪纺蕾丝衫':'雪纺蕾丝',
         }
         print(y['title'],y['title'] in change_category)
         if(y['title'] in change_category):
             y['title'] = change_category.get(y['title'])
         sql = "SELECT * FROM goods_category WHERE title = '%s'" % (y['title'])
         #print(sql)
         db_category  = cursor.execute(sql)
         #print(db_category)
         if(db_category):
             results = cursor.fetchall()
             for row in results:
                 print(row, sep='\t')
                 print(row[0])
                 if(row[1] !='0'):
                     img = requests.get(y['pic'])
                     # imgName = 'img/category/' + y['title'].replace('/','') + str(y['element_id']) + '.jpg'
                     imgName = 'category-lavarel/' + str(row[0]) + '.jpg'
                     with open(imgName, 'ab') as f:
                         f.write(img.content)
                         f.close()
                     print(imgName)



t = time.time()


# 关闭数据库连接
db.close()