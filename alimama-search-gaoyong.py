#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     alimama-search-gaoyong.py
   Description :    功能说明
   淘宝联盟选品库添加 仅适用于高佣活动搜索
   Author :       david
   date：          2018/10/12
-------------------------------------------------
   Change Activity:
                   2018/10/12:
-------------------------------------------------
"""


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

        self.web.get('https://pub.alimama.com/promo/item/channel/index.htm?channel=qqhd')
        time.sleep(4)
        cookie = ''
        for elem in self.web.get_cookies():
            cookie += elem["name"] + "=" + elem["value"] + ";"
            if elem["name"] == '_tb_token_':
                self.token = elem["value"]
        self.cookies = cookie
        self.headers['Cookie'] = self.cookies
        # self.web.quit()
    # 搜索
    def search(self,keyword):
        # self._input_simulation(self.web.find_element_by_id('q'), keyword)
        q = self.web.find_element_by_id('q')
        q.clear()
        q.send_keys(keyword)
        # self.web.find_element_by_class_name('btn btn-brand search-btn').click()
        self.web.find_element_by_class_name('search-btn-channel').click()
        time.sleep(2)
        # dpyhg = self.web.find_element_by_id('dpyhq').click()
        dpyhg = self.web.find_element_by_id('dpyhq')

        # dpyhg.click()
        dpyhg.send_keys(Keys.ENTER)
        time.sleep(4)

        # 模拟鼠标划动
        action = ActionChains(self.web)
        action.click_and_hold(dpyhg).perform()
        action.reset_actions()
        ActionChains(self.web).move_by_offset(xoffset=5, yoffset=0).perform()
        action.release().perform()
        action.reset_actions()

        time.sleep(1)
        # 月销80笔以上的
        # self.web.find_element_by_name('startBiz30day')
        # self.web.find_element_by_name('startBiz30day').click()
        # self.web.find_element_by_name('startBiz30day').send_keys('80')
        # self.web.find_element_by_name('startBiz30day').find_element_by_xpath("../span[@class='btn btn-brand btn-small ml5']").click()


        time.sleep(random.randint(4, 7))
        has_pagenation = True
        current_page = '1'

        while has_pagenation:
            print('第' + current_page + '页')
            # 搜索结果页面上的产品加入选品库
            selection_filter = self._search_result_filter()
            if self.isElementExist("//a[@class='btn btn-xlarge btn-current']"):
                current_page = self.web.find_element_by_xpath("//a[@class='btn btn-xlarge btn-current']").text
                next_page = self.web.find_element_by_xpath("//div[@class='go']/input").get_attribute('value')
                has_pagenation = current_page != next_page
            else:
                has_pagenation = False
            if has_pagenation != True:
                break
            if selection_filter:
                break
            # 下一页
            self.web.find_element_by_xpath("//a[@class='btn-last btn btn-xlarge btn-white']").send_keys(Keys.ENTER)
            time.sleep(random.randint(5, 15))
            current_page = self.web.find_element_by_xpath("//a[@class='btn btn-xlarge btn-current']").text
            next_page = self.web.find_element_by_xpath("//div[@class='go']/input").get_attribute('value')

    # 判断元素是否存在
    def isElementExist(self, element):
        flag = True
        try:
            self.web.find_element_by_xpath(element)
            return flag
        except:
            flag = False
            return flag


    # 搜索结果检索添加
    def _search_result_filter(self):
        if self.selection_count >= 200:
            return True
        search_result = self.web.find_elements_by_class_name('block-search-box')
        # print(len(search_result))
        # print(search_result)
        i = 0
        for product in search_result:
            # product.find_element_by_class_name('money').find_element_by_tag_name('span').text
            i = i + 1
            # print(i)
            # 产品名称
            product_name = product.find_element_by_xpath(
                ".//div[@class='content-line']/p/a[@class='color-m content-title']").get_attribute('title')
            # 优惠券价格
            coupon_money = product.find_element_by_xpath(
                ".//div[@class='box-content']/div[@class='content-line tags-container']/span[@class='tag tag-coupon']/span[@class='money']/span").text

            if int(coupon_money) >= 10:  # 大于等于10元
                print(coupon_money, '-------', product_name)
                # print('大于等于10元')
                # product.find_element_by_xpath(".//div[@class='box-btn-group']/a[@class='box-btn-right']").click()
                product.find_element_by_xpath(".//div[@class='box-btn-group']/a[@class='box-btn-right']").send_keys(
                    Keys.ENTER)
                # 选品库数量+1
                self.selection_count = self.selection_count + 1
                # print(product.find_element_by_xpath(".//div[@class='box-btn-group']/a[@class='box-btn-right']").text)
            # print(product.find_element_by_xpath("//div[@class='box-content']/div[@class='content-line tags-container']/span[@class='tag tag-coupon']/span[@class='money']/span").text)
            # 选品库达到200时退出选品
            if self.selection_count >= 200:
                break
                return True
        return False

    # 加入选品库
    def add_selection(self, selection_name):
        # 点击加入选品库
        c = self.web.find_element_by_xpath("//a[@class='btn-brand add-selection']").click()
        time.sleep(1.5)
        selection_libs = self.web.find_elements_by_xpath("//ul[@class='selection-add-bd']/li")
        for selection_lib in selection_libs:
            selection_lib_name = selection_lib.find_element_by_xpath(".//h5/span").text

            if(selection_name == selection_lib_name):
                print('======选中这个=====', selection_lib_name)
                selection_lib.click()
                time.sleep(1)
                print(self.web.find_element_by_xpath("//div[@class='dialog-ft']/button[1]").text)
                # 添加到选品库
                self.web.find_element_by_xpath("//div[@class='dialog-ft']/button[1]").click()
                # 选品库数量归0
                self.selection_count = 0
                time.sleep(1)
                # 继续选品
                self.web.find_element_by_xpath("//div[@class='dialog-ft dialog-add-ok']/span[2]").click()
                break

    # 模拟输入
    def _input_simulation(e, text):
        for i in range(len(text)):
            sleep_time = random.randint(8, 30)
            time.sleep(int(sleep_time / 10))
            e.send_keys(text[i])

    # 获取淘宝客订单列表
    def get_taoke_order_list(self):
        s_day = datetime.date.today() - datetime.timedelta(days=90)
        e_day = datetime.date.today() - datetime.timedelta(days=1)
        url = 'https://pub.alimama.com/report/getTbkPaymentDetails.json?startTime=' + s_day.strftime(
            "%Y-%m-%d") + '&endTime=' + e_day.strftime(
            "%Y-%m-%d") + '&payStatus=&queryType=1&toPage=1&perPageSize=20'
        print(url)
        web_data = self.req.get(url, headers=self.headers)
        data = json.loads(web_data.text)
        print(data)

    # post数据 添加选品库
    def post_tk_produt_item(self, groupId, itemListStr, pvid):
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
    """ """
    categorys =[
        # ['分类','子类','关键词'],
        # ['女装','女装','女装'],
        # ['男装','男装','男装'],
        # ['配饰','配饰','配饰'],
        # ['运动','运动','运动'],
        # ['家纺','家纺','家纺'],
        # ['家电','家电','家电'],
        # ['箱包','箱包','箱包'],
        ['数码','数码','数码'],
        ['母婴','母婴','母婴'],
        ['女鞋','女鞋','女鞋'],
        ['百货','百货','百货'],
        ['个护','个护','个护'],
        ['内衣','内衣','内衣'],
        ['食品','食品','食品'],
        ['美妆','美妆','美妆'],
        # ['美妆','眼妆','眼妆']
        ]


    sp = Spider()
    sp.login()

    for category in categorys:
        print('《-------搜索 ' + category[1] + ' 开始------》')
        sp.search(category[2])  # 关键词搜索
        sp.add_selection(category[1])  # 加加入对应选品库
        print('《-------搜索 ' + category[1] + ' 结束------》')
        time.sleep(random.randint(10, 20))

    # print('搜索 女装 开始')
    # sp.search('女装') # 关键词搜索
    # sp.add_selection('女装') # 加加入对应选品库
    # sp.web.close()
    print('添加选品完成 关闭')
    # while True:
        # sp.get_taoke_order_list()
        # time.sleep(30)

    # pvid = ''
    # rs = sp.post_tk_produt_item('18509107', '563078519787', pvid)
    # print(rs.content)