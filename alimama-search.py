#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     alimama-search.py
   Description :    功能说明
   淘宝联盟选品库添加 仅适用于搜索
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
    # 搜索
    def search(self,keyword):
        # self._input_simulation(self.web.find_element_by_id('q'), keyword)
        q = self.web.find_element_by_id('q')
        q.clear()
        q.send_keys(keyword)
        # self.web.find_element_by_class_name('btn btn-brand search-btn').click()
        self.web.find_element_by_class_name('search-btn').click()
        time.sleep(2)
        self.web.find_element_by_id('dpyhq').click()
        self.web.find_element_by_id('hPayRate30').click()
        time.sleep(random.randint(15, 20))

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
            time.sleep(random.randint(15, 20))
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
                # print(coupon_money)
                # print(product_name)
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
            # print(selection_lib_name)
            if(selection_name == selection_lib_name):
                print('======选品库选中这个=====',selection_name, self.selection_count, '件商品====')
                selection_lib.click()
                time.sleep(1)
                # print(self.web.find_element_by_xpath("//div[@class='dialog-ft']/button[1]").text)
                # 添加到选品库
                self.web.find_element_by_xpath("//div[@class='dialog-ft']/button[1]").click()
                print('完成选品库，继续选品')
                # 选品库数量归0
                self.selection_count = 0
                time.sleep(1)
                # 继续选品
                self.web.find_element_by_xpath("//div[@class='dialog-ft dialog-add-ok']/span[2]").click()
                time.sleep(3)
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

    # 更新数据库中分类为未更新
    def update_db_category(self,category):
        try:
            # 打开数据库连接
            db = pymysql.connect(DB_HOST, DB_USER, DB_PASSWORD, DB_NAME, charset="utf8")

            # 使用cursor()方法获取操作游标
            cursor = db.cursor()

            # 生成SQL
            sql = "UPDATE goods_category set updated_goods = 0 WHERE title = '%s'" % (category)
            print(sql)
            # 执行sql语句
            cursor.execute(sql)
            # 执行sql语句
            db.commit()
            # 关闭数据库连接
            db.close()
        except Exception as e:
            print('发生异常：', e)
            # 发生错误时回滚
            db.rollback()
            # 关闭数据库连接
            db.close()


if __name__ == '__main__':

    """
    ['分类','子类','关键词'],
    ['女装','卫衣','女装卫衣'],
    ['女装','衬衫','女装衬衫'],
    ['女装','雪纺蕾丝','雪纺蕾丝'],
    ['女装','针织衫','针织衫女'],
    """
    categorys = [
        # ['分类', '子类', '关键词'],
        # ['女装', '女装-卫衣', '女装卫衣'],
        # ['女装', '女装-衬衫', '女装衬衫'],
        # ['女装', '女装-雪纺蕾丝', '雪纺蕾丝'],
        # ['女装', '女装-针织衫', '针织衫女'],
        # ['女装', '女装-外套', '外套女'],
        # ['女装', '女装-牛仔衣', '牛仔衣女'],
        # ['女装', '女装-防晒服', '防晒服女'],
        # ['女装', '女装-裤装', '裤子女'],
        # ['女装', '女装-牛仔裤', '牛仔裤女'],
        # ['女装', '女装-休闲裤', '休闲裤女'],
        # ['女装', '女装-打底裤', '打底裤'],
        # ['女装', '女装-短裤', '短裤女'],
        # ['女装', '女装-情侣装', '情侣装'],
        # ['女装', '女装-妈妈装', '妈妈装'],
        # ['女装', '女装-吊带背心', '吊带背心'],
        # ['美妆', '美妆-眉妆', '眉妆'],
        # ['美妆', '美妆-美瞳', '美瞳'],
        # ['美妆', '美妆-面膜', '面膜'],
        # ['美妆', '美妆-护肤套装', '护肤套装女'],
        # ['美妆', '美妆-卸妆洁面', '卸妆洁面'],
        # ['美妆', '美妆-面部护理', '面部护理'],
        # ['美妆', '美妆-网红眼影', '眼影'],
        # ['美妆', '美妆-美妆工具', '美妆工具'],
        # ['美妆', '美妆-男士护肤', '男士护肤'],
        # ['食品', '食品-休闲食品', '休闲食品'],
        # ['食品', '食品-坚果', '坚果'],
        # ['食品', '食品-辣味', '辣味'],
        # ['食品', '食品-糕点饼干', '糕点饼干'],
        # ['食品', '食品-方便速食', '方便速食'],
        # ['食品', '食品-新鲜水果', '水果'],
        # ['食品', '食品-茶水冲饮', '茶饮'],
        # ['食品', '食品-茶水冲饮', '茶饮'],
        # ['食品', '食品-米面', '米面'],

        # ['女装', '女装', '女装'],
        # ['女装', '女装-外套', '外套女'],
        # ['女装', '女装-牛仔衣', '牛仔衣女'],
        # ['女装', '女装-防晒服', '防晒服女'],
        # ['女装', '女装-裤装', '裤子女'],
        # ['女装', '女装-牛仔裤', '牛仔裤女'],
        # ['女装', '女装-休闲裤', '休闲裤女'],
        # ['女装', '女装-打底裤', '打底裤'],
        # ['女装', '女装-短裤', '短裤女'],
        # ['女装', '女装-连衣裙', '连衣裙'],
        # ['女装', '女装-半身裙', '半身裙'],
        # ['女装', '女装-吊带背心', '吊带背心'],
        # ['女装', '女装-情侣装', '情侣装'],
        # ['女装', '女装-妈妈装', '妈妈装'],
        # ['女装', '女装-套装', '套装女'],
        # ['女装', '女装-T恤', 'T恤女'],
        # ['女装', '女装-卫衣', '卫衣女'],
        # ['女装', '女装-衬衫', '衬衫女'],
        # ['女装', '女装-雪纺蕾丝', '雪纺蕾丝'],
        # ['女装', '女装-针织衫', '针织衫女'],
        # ['美妆', '美妆', '化妆品'],
        # ['美妆', '美妆-眉妆', '眉妆'],
        # ['美妆', '美妆-美瞳', '美瞳'],
        # ['美妆', '美妆-面膜', '面膜'],
        # ['美妆', '美妆-护肤套装', '护肤品套装'],
        # ['美妆', '美妆-卸妆洁面', '卸妆洁面'],
        # ['美妆', '美妆-面部护理', '面部护理'],
        # ['美妆', '美妆-网红眼影', '眼影'],
        # ['美妆', '美妆-美妆工具', '美妆工具'],
        # ['美妆', '美妆-男士护肤', '男士护肤'],
        # ['美妆', '美妆-底妆', '底妆'],
        # ['美妆', '美妆-唇妆', '唇妆'],
        # ['美妆', '美妆-眼妆', '眼妆'],
        # ['食品', '食品', '食品'],
        # ['食品', '食品-休闲食品', '休闲食品'],
        # ['食品', '食品-坚果', '坚果'],
        # ['食品', '食品-辣味', '辣味'],
        # ['食品', '食品-糕点饼干', '糕点饼干'],
        # ['食品', '食品-方便速食', '方便速食'],
        # ['食品', '食品-新鲜水果', '水果'],
        # ['食品', '食品-茶水冲饮', '茶饮'],
        # ['食品', '食品-米面', '米面'],
        # ['食品', '食品-饮料酒水', '饮料'],
        # ['食品', '食品-营养保健', '营养品'],
        # ['食品', '食品-糖果奶酪', '糖果'],
        # ['食品', '食品-地方特产', '地方特产'],
        # ['内衣', '内衣', '内衣'],
        # ['内衣', '内衣-文胸', '文胸'],
        # ['内衣', '内衣-内裤', '内裤'],
        # ['内衣', '内衣-家居服', '家居服'],
        # ['内衣', '内衣-袜子', '袜子'],
        # ['内衣', '内衣-丝袜', '丝袜'],
        # ['内衣', '内衣-抹胸背心', '抹胸背心'],
        # ['内衣', '内衣-塑身', '塑身'],
        # ['内衣', '内衣-文胸套装', '文胸套装'],
        # ['内衣', '内衣-基础打底', '基础打底'],
        # ['个护', '个护', '个护'],
        # ['个护', '个护-洗发护发', '洗发护发'],
        # ['个护', '个护-身体护理', '身体护理'],
        # ['个护', '个护-毛巾浴巾', '毛巾浴巾'],
        # ['个护', '个护-电动牙刷', '电动牙刷'],
        # ['个护', '个护-口腔清洁', '口腔清洁'],
        # ['个护', '个护-美容工具', '美容工具'],
        # ['个护', '个护-手部护理', '手部护理'],
        # ['个护', '个护-足部护理', '足部护理'],
        # ['百货', '百货', '百货'],
        # ['百货', '百货-纸巾', '纸巾'],
        # ['百货', '百货-衣物清洁', '衣物清洁'],
        # ['百货', '百货-清洁工具', '清洁工具家用'],
        # ['百货', '百货-鞋子清洁', '鞋子清洁'],
        # ['百货', '百货-杀虫驱蚊', '杀虫驱蚊'],
        # ['百货', '百货-洁厕用品', '洁厕'],
        # ['百货', '百货-日用杂货', '日用百货 家用'],
        # ['百货', '百货-厨房用品', '厨房用品'],
        # ['百货', '百货-车品装饰', '车品装饰'],
        # ['百货', '百货-乐器', '乐器'],
        # ['百货', '百货-图书杂志', '图书'],
        # ['百货', '百货-纸品文具', '文具'],
        # ['百货', '百货-绿植花卉', '绿植'],
        # ['百货', '百货-收纳神器', '收纳'],
        # ['女鞋', '女鞋', '女鞋'],
        # ['女鞋', '女鞋-小皮鞋', '小皮鞋女'],
        # ['女鞋', '女鞋-休闲鞋', '休闲鞋女'],
        # ['女鞋', '女鞋-帆布鞋', '帆布鞋女'],
        # ['女鞋', '女鞋-平底鞋', '平底鞋女'],
        # ['女鞋', '女鞋-高跟鞋', '高跟鞋'],
        # ['女鞋', '女鞋-凉鞋', '凉鞋女'],
        # ['女鞋', '女鞋-运动鞋', '运动鞋女'],
        # ['女鞋', '女鞋-靴子', '靴子女'],
        # ['女鞋', '女鞋-妈妈鞋', '妈妈鞋'],
        # ['母婴', '母婴', '母婴'],
        # ['母婴', '母婴-产前产后', '产前产后'],
        # ['母婴', '母婴-孕产妇用品', '孕产妇用品'],
        # ['母婴', '母婴-孕妇服', '孕妇装'],
        ['母婴', '母婴-玩具玩偶', '玩具玩偶'],
        ['母婴', '母婴-婴儿服装', '婴儿服装'],
        ['母婴', '母婴-婴儿用品', '婴儿用品'],
        ['母婴', '母婴-婴儿食品', '婴儿食品'],
        ['母婴', '母婴-早教益智', '早教益智玩具'],
        ['母婴', '母婴-尿布湿', '尿布湿'],
        ['母婴', '母婴-奶瓶', '奶瓶'],
        ['母婴', '母婴-奶粉', '奶粉'],
        # ['数码', '数码', '数码'],
        # ['数码', '数码-电脑外设', '电脑外设'],
        # ['数码', '数码-智能设备', '智能设备'],
        # ['数码', '数码-手机电脑', '手机电脑'],
        # ['数码', '数码-手机壳', '手机壳'],
        # ['数码', '数码-手机膜', '手机膜'],
        # ['数码', '数码-数据线', '数据线'],
        # ['数码', '数码-麦克风', '麦克风'],
        # ['数码', '数码-游戏设备', '游戏设备'],
        # ['数码', '数码-影音娱乐', '影音娱乐'],
        # ['数码', '数码-耳机', '耳机'],
        # ['数码', '数码-移动电源', '移动电源'],
        # ['箱包', '箱包', '箱包'],
        # ['箱包', '箱包-网红同款', '网红同款'],
        # ['箱包', '箱包-单肩包', '单肩包'],
        # ['箱包', '箱包-钱包', '钱包'],
        # ['箱包', '箱包-双肩包', '双肩包'],
        # ['箱包', '箱包-旅行箱', '旅行箱'],
        # ['箱包', '箱包-日韩潮包', '日韩潮包'],
        # ['家电', '家电', '家电'],
        # ['家电', '家电-生活电器', '生活电器'],
        # ['家电', '家电-厨房电器', '厨房电器'],
        # ['家电', '家电-大家电', '大家电'],
        # ['家电', '家电-吸尘除螨', '吸尘除螨'],
        # ['家电', '家电-挂烫机', '挂烫机'],
        # ['家电', '家电-电饭锅', '电饭锅'],
        # ['家电', '家电-烘烤电器', '烘烤电器'],
        # ['家电', '家电-榨汁机', '榨汁机'],
        # ['家电', '家电-热水壶', '热水壶'],
        # ['家电', '家电-电磁炉', '电磁炉'],
        # ['家电', '家电-宿舍必备', '宿舍必备'],
        # ['家纺', '家纺', '家纺'],
        # ['家纺', '家纺-床品套件', '床品套件'],
        # ['家纺', '家纺-枕头被褥', '枕头被褥'],
        # ['家纺', '家纺-沙发套件', '沙发套件'],
        # ['家纺', '家纺-地毯地垫', '地毯地垫'],
        # ['家纺', '家纺-卧室家具', '卧室家具'],
        # ['家纺', '家纺-客厅家具', '客厅家具'],
        # ['家纺', '家纺-家居饰品', '家居饰品'],
        # ['家纺', '家纺-五金灯具', '五金灯具'],
        # ['家纺', '家纺-厨卫用品', '厨卫用品'],
        # ['运动', '运动', '运动'],
        # ['运动', '运动-骑行轮滑', '骑行轮滑'],
        # ['运动', '运动-户外装备', '户外装备'],
        # ['运动', '运动-野营旅行', '野营旅行'],
        # ['运动', '运动-健身器材', '健身器材'],
        # ['运动', '运动-体育用品', '体育用品'],
        # ['运动', '运动-游泳', '游泳'],
        # ['运动', '运动-瑜伽', '瑜伽'],
        # ['运动', '运动-垂钓装备', '垂钓装备'],
        # ['配饰', '配饰', '配饰'],
        # ['配饰', '配饰-手链脚链', '手链脚链'],
        # ['配饰', '配饰-时尚手表', '时尚手表'],
        # ['配饰', '配饰-日韩发饰', '日韩发饰'],
        # ['配饰', '配饰-网红耳饰', '网红耳饰'],
        # ['配饰', '配饰-服装配件', '服装配件'],
        # ['配饰', '配饰-精美颈饰', '精美颈饰'],
        # ['配饰', '配饰-眼镜', '眼镜'],
        # ['男装', '男装', '男装'],
        # ['男装', '男装-T恤', 'T恤'],
        # ['男装', '男装-衬衫', '衬衫'],
        # ['男装', '男装-卫衣', '卫衣'],
        # ['男装', '男装-休闲裤', '休闲裤'],
        # ['男装', '男装-运动裤', '运动裤'],
        # ['男装', '男装-牛仔裤', '牛仔裤'],
        # ['男装', '男装-夹克', '夹克'],
        # ['男装', '男装-休闲套装', '休闲套装'],
        # ['男装', '男装-短裤', '短裤'],
        # ['男装', '男装-POLO衫', 'POLO衫'],
        # ['男装', '男装-职业套装', '职业套装'],
        # ['男装', '男装-工装制服', '工装制服'],
        # ['男装', '男装-中老年', '中老年']
    ]


    sp = Spider()  # 实例化浏览器
    sp.login()  # 登录淘宝

    for category in categorys:
        print('《-------搜索 ' + category[1] + ' 开始------》')
        sp.search(category[2])  # 关键词搜索
        sp.add_selection(category[1])  # 加加入对应选品库

        # 获取子类名字
        child_category = category[1].split('-')
        if len(child_category) == 2:
            child = child_category[1]
        else:
            child = child_category[0]

        sp.update_db_category(child) # 更新数据库中对应分类为 未更新

        print('《-------搜索 ' + category[1] + ' 结束------》')
        time.sleep(random.randint(20, 40))







    # print('搜索 女装-针织衫女 开始')
    # sp.search('针织衫女') # 关键词搜索
    # sp.add_selection('女装-针织衫') # 加加入对应选品库
    sp.web.close()
    print('添加选品完成 关闭')
    # while True:
        # sp.get_taoke_order_list()
        # time.sleep(30)

    # pvid = ''
    # rs = sp.post_tk_produt_item('18509107', '563078519787', pvid)
    # print(rs.content)