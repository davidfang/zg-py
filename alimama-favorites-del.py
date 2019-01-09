#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     alimama-favorites-del.py
   Description :    功能说明
   淘宝联盟选品库删除
   Author :       david
   date：          2018/10/12
-------------------------------------------------
   Change Activity:
                   2018/10/12:
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

import datetime
import json
import time
import random
import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

class Spider(object):
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

        self.web.get('https://pub.alimama.com/manage/selection/list.htm')
        time.sleep(4)
        cookie = ''
        for elem in self.web.get_cookies():
            cookie += elem["name"] + "=" + elem["value"] + ";"
            if elem["name"] == '_tb_token_':
                self.token = elem["value"]
        self.cookies = cookie
        self.headers['Cookie'] = self.cookies
        # self.web.quit()


    # 判断元素是否存在
    def isElementExist(self, element):
        flag = True
        try:
            self.web.find_element_by_xpath(element)
            return flag
        except:
            flag = False
            return flag





    # 模拟输入
    def _input_simulation(e, text):
        for i in range(len(text)):
            sleep_time = random.randint(8, 30)
            time.sleep(int(sleep_time / 10))
            e.send_keys(text[i])

    #选品库
    def favorite(self):
        has_pagenation = True
        current_page = '1'

        while has_pagenation:
            print('选品库 第' + current_page + '页')
            time.sleep(3)
            # 选品库列表页面
            self.favorites_list()

            if self.isElementExist("//a[@class='btn btn-xlarge btn-current']"):
                current_page = self.web.find_element_by_xpath("//a[@class='btn btn-xlarge btn-current']").text
                next_page = self.web.find_element_by_xpath("//div[@class='go']/input").get_attribute('value')
                has_pagenation = current_page != next_page
            else:
                has_pagenation = False
            if has_pagenation != True:
                break
            # 下一页
            self.web.find_element_by_xpath("//a[@class='btn-last btn btn-xlarge btn-white']").send_keys(Keys.ENTER)
            time.sleep(random.randint(15, 20))
            current_page = self.web.find_element_by_xpath("//a[@class='btn btn-xlarge btn-current']").text
            next_page = self.web.find_element_by_xpath("//div[@class='go']/input").get_attribute('value')

    # 选品库列表页面
    def favorites_list(self):
        p = self.web.find_elements_by_xpath("//div[@class='item fl']")
        for element in p:
            # print(element)
            favorite_name = element.find_element_by_xpath('.//a/h5/span').text
            favorite_count = element.find_element_by_xpath('.//a/div/span/span').text

            if favorite_count != '0':
                print(favorite_name, favorite_count)
                element.find_element_by_xpath('.//a').click()
                self.favorites_page()

    # 选品页面
    def favorites_page(self):
        time.sleep(3)
        # 选品库列表页面
        self.favorite_items()
        self.web.find_element_by_xpath("//a[@class='rtn-icon pubfont color-l']").click()
        self.favorite()



    # 选品 具体产品列表
    def favorite_items(self):
        items = self.web.find_elements_by_class_name('tag-wrap')

        while self.isElementExist("//tr['tag-wrap']/td[@class='left']/div/ul/li/a"):

        # for item in items:
            item_name = self.web.find_element_by_xpath("//tr['tag-wrap']/td[@class='left']/div/ul/li/a").text
            # item_name = item.find_element_by_xpath(".//td[@class='left'][1]/div[@class='block-list-group tag-wrap block-list-group-event']/ul/li/a/span").text
            print(item_name)

            item = self.web.find_element_by_xpath("//tr['tag-wrap']")
            del_td = self.web.find_element_by_xpath("//tr['tag-wrap']/td[@class='center']")
            del_button = self.web.find_element_by_xpath("//tr['tag-wrap']/td[@class='center']/div[@class='operation']/button[@class='btn btn-small btn-gray mt10']")
            ActionChains(self.web).move_to_element(del_td).click(del_button).perform()
            # ActionChains(self.web).move_to_element(item).perform()
            # item.click()
            # time.sleep(2)
            #
            # del_button.click()
            # # ActionChains(self.web).move_to_element(del_td).click(del_button).perform()
            self.web.find_element_by_xpath("//div[@class='table-operation-mask selection-mask']/div[@class='operation']/button[@class='btn btn-brand w100']").click()

            time.sleep(3)








    # post数据 添加选品库
    def post_tk_produt_item_add(self, groupId, itemListStr, pvid):
        url = 'https://pub.alimama.com/favorites/item/batchAdd.json'
        data = {
            'groupId': groupId, # 18509107,
            'itemListStr': itemListStr, # 560254275938,
            't': int(time.time() * 1000),
            '_tb_token_': self.token,
            'pvid': pvid,


        }
        headers = self.headers
        headers = headers.update({
            'Content-Length': str(len(json.dumps(data))),
            'Origin': 'http://pub.alimama.com',
            'Referer': 'http://pub.alimama.com/promo/search/index.htm',
        })
        res = self.req.post(url, headers=headers, data=data)
        return res

    # post数据 添加选品库
    def post_tk_produt_item_del(self, groupId, itemListStr, pvid):
        url = 'https://pub.alimama.com/favorites/item/batchAdd.json'
        data = {
            'groupId': groupId, # 18509107,
            'itemListStr': itemListStr, # 560254275938,
            't': int(time.time() * 1000),
            '_tb_token_': self.token,
            'pvid': pvid,


        }
        headers = self.headers
        headers = headers.update({
            'Content-Length': str(len(json.dumps(data))),
            'Origin': 'http://pub.alimama.com',
            'Referer': 'http://pub.alimama.com/promo/search/index.htm',
        })
        res = self.req.post(url, headers=headers, data=data)
        return res



if __name__ == '__main__':



    sp = Spider()  # 实例化浏览器
    sp.login()  # 登录淘宝

    # for category in categorys:
    #     print('《------- ' + category[1] + ' 开始------》')
    #
    #     print('《-------搜索 ' + category[1] + ' 结束------》')
    #     time.sleep(random.randint(20, 40))
    # rs = sp.post_tk_produt_item_add('18509448', '563078519787', '')
    #     # print(rs.content)

    sp.favorite()


    sp.web.close()
    print('删除选品 关闭')