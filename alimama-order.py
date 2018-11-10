#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     alimama-order.py
   Description :    订单处理
   Author :       david
   date：          2018/11/2
-------------------------------------------------
   Change Activity:
                   2018/11/2:
-------------------------------------------------
"""
from dotenv import load_dotenv,find_dotenv
import os

import pymysql
#加载配置文件
load_dotenv(find_dotenv())
DB_HOST= os.getenv('DB_HOST')
DB_PORT=os.getenv('DB_PORT')
DB_USER=os.getenv('DB_USER')
DB_PASSWORD=os.getenv('DB_PASSWORD')
DB_NAME=os.getenv('DB_NAME')

from sqlalchemy import create_engine  #引入sqlalchemy   #引擎
import datetime
import json
import time
import random
import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import pandas as pd

class Order(object):
    def __init__(self, download_dir):
        options = webdriver.ChromeOptions()
        prefs = {
            'profile.default_content_settings.popups': 0,
            'download.default_directory': download_dir
        }
        options.add_experimental_option('prefs', prefs)


        self.web = webdriver.Chrome(chrome_options=options)
        # self.web = webdriver.Chrome()
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

        self.web.get('https://pub.alimama.com/myunion.htm?#!/report/detail/taoke')
        time.sleep(4)
        cookie = ''
        for elem in self.web.get_cookies():
            cookie += elem["name"] + "=" + elem["value"] + ";"
            if elem["name"] == '_tb_token_':
                self.token = elem["value"]
        self.cookies = cookie
        self.headers['Cookie'] = self.cookies
        # self.web.quit()

    '''
        web.get('https://pub.alimama.com/promo/search/index.htm')
        time.sleep(4)
        cookie = ''
        for elem in self.web.get_cookies():
            cookie += elem["name"] + "=" + elem["value"] + ";"
            if elem["name"] == '_tb_token_':
                token = elem["value"]
        cookies = cookie
        headers['Cookie'] = cookies
    '''

    # 订单数据入库
    def in_database(self, from_file_name, to_file_name):
        rename_columns = {'订单编号':'trade_id',#淘宝订单号
            '商品ID':'num_iid',#商品ID
            '商品信息':'item_title',#商品标题
            '商品数':'item_num',#商品数量
            '商品单价':'price',#单价
            '掌柜旺旺':'seller_nick',#卖家昵称
            '所属店铺':'seller_shop_title',#卖家店铺名称
            '预估收入':'commission',# 推广者获得的收入金额，对应联盟后台报表“预估收入”
            '分成比率':'commission_rate',#推广者获得的分成比率，对应联盟后台报表“分成比率”
            '创建时间':'create_time',#淘客订单创建时间
            '结算时间':'earning_time',#淘客订单结算时间
            '订单状态':'tk_status',#淘客订单状态，3：订单结算，12：订单付款， 13：订单失效，14：订单成功
            '第三方服务来源':'tk3rd_type',#第三方服务来源，没有第三方服务，取值为“--”
            '订单类型':'order_type',#订单类型，如天猫，淘宝
            '收入比率':'income_rate',#收入比率，卖家设置佣金比率+平台补贴比率
            '效果预估':'pub_share_pre_fee',#效果预估，付款金额*(佣金比率+补贴比率)*分成比率
            '补贴比率':'subsidy_rate',#补贴比率
            '补贴类型':'subsidy_type',#补贴类型，天猫:1，聚划算:2，航旅:3，阿里云:4
            '成交平台':'terminal_type',#成交平台，PC:1，无线:2
            '类目名称':'auction_category',#类目名称
            '来源媒体ID':'site_id',#来源媒体ID
            '来源媒体名称':'site_name',#来源媒体名称
            '广告位ID':'adzone_id',#广告位ID
            '广告位名称':'adzone_name',#广告位名称
            '付款金额':'alipay_total_price',#付款金额
            '佣金比率':'total_commission_rate',#佣金比率
            '佣金金额':'total_commission_fee',#佣金金额
            '补贴金额':'subsidy_fee',#补贴金额
            '渠道关系ID':'relation_id',
             '点击时间':'click_time',#点击时间
             '结算金额':'settlement_amount',#结算金额
             '技术服务费比率':'technical_service_fee_ratio'#技术服务费比率
                          }
        # del_columns = []
        data = pd.read_excel(from_file_name)
        # data = data.drop(columns=del_columns)
        data = data.rename(columns=rename_columns)
        data[['trade_id','site_id','num_iid','adzone_id']] = data[['trade_id','site_id','num_iid','adzone_id']].astype('str')
        # data = data.applymap(str)
        print(data)
        print(data['trade_id'].astype('str'))
        data.to_excel(to_file_name, 'Sheet1', index=False)
        # 输入到数据库
        # str_mysql_connect = 'mysql+pymysql://%s:%s@%s:%s/%s?charset=utf8' % (DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME)
        #
        # yconnect = create_engine(str_mysql_connect)
        # data.to_sql('order2', con=yconnect, if_exists='replace', index=False)
        pass

    # 下载订单列表excel
    def download_order_list_excel(self):
        self.web.find_element_by_xpath("//div[@class='chg-guide-img1']/span[@class='close-icon']").click()
        time.sleep(3)
        t = self.web.find_element_by_xpath("//div[@class='table-settings']/a[@class='btn btn-size25']")
        t.click()
        print(t.get_attribute('title'))

    # 获取淘宝客订单列表 json
    def get_taoke_order_list(self):
        s_day = datetime.date.today() - datetime.timedelta(days=90)
        e_day = datetime.date.today() - datetime.timedelta(days=1)
        url = 'https://pub.alimama.com/report/getTbkPaymentDetails.json?startTime=' + s_day.strftime(
            "%Y-%m-%d") + '&endTime=' + e_day.strftime(
            "%Y-%m-%d") + '&payStatus=&queryType=1&toPage=1&perPageSize=20'
        print(url)
        web_data = self.req.get(url, headers=self.headers)


        data = json.loads(web_data.text)


        print(data['data']['paymentList'])
        pass
        # json_paymentList = data['data']['paymentList']
        # pd_paymentList = pd.DataFrame(json_paymentList)
        # print(pd_paymentList)
        # str_mysql_connect = 'mysql+pymysql://%s:%s@%s:%s/%s?charset=utf8' % (DB_USER,DB_PASSWORD,DB_HOST,DB_PORT,DB_NAME)
        # print(str_mysql_connect)
        # yconnect = create_engine(str_mysql_connect)
        # pd_paymentList.to_sql('order4', con=yconnect, if_exists='replace', index=False)
        # #print(data.data.paymentList)

if __name__ == '__main__':
    download_dir = '/Users/david/Work/dnmp/www/hst-lv/storage/app/public/'
    order = Order(download_dir=download_dir)
    order.login()
    order.download_order_list_excel()
    time.sleep(5)
    # taokeDetail = "TaokeDetail-2018-11-10.xls"
    taokeDetail = datetime.date.today().strftime("TaokeDetail-%Y-%m-%d.xls")
    # order.get_taoke_order_list()  # 不用了
    from_file_name = download_dir + taokeDetail
    to_file_name = download_dir + 'new-' + taokeDetail
    print(taokeDetail)
    order.in_database(from_file_name, to_file_name)

    # order.web.close()
    pass