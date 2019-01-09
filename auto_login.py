#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     auto_login.py
   Description :    淘宝联盟自动登录
   Author :       david
   date：          2018/10/12
-------------------------------------------------
   Change Activity:
                   2018/10/12:
-------------------------------------------------
"""
import random
import time
import selenium
from selenium.webdriver.common.action_chains import ActionChains

# 模拟输入
def _input_simulation(e, text):
    for i in range(len(text)):
        sleep_time = random.randint(8, 30)
        time.sleep(int(sleep_time / 10))
        e.send_keys(text[i])


# 判断是否有滑动验证
def _has_move(device):
    yanzhen = device.find_element_by_id('nocaptcha')
    style = yanzhen.get_attribute('style')
    if style == 'display: block;':
        return True
    return False

# 模拟滑动
def _move_simulation(device, e):
    try:
        action = ActionChains(device)
        action.click_and_hold(e).perform()
        action.reset_actions()
        offset = 21
        #for i in range(int(210 / offset)):
        for i in range(20):
            ActionChains(device).move_by_offset(xoffset=2, yoffset=0).perform()
            time.sleep(int((offset - i) / 50))
        action.release().perform()
        action.reset_actions()

        #device.find_element_by_class_name()

    except Exception as e:
        if DEBUG: print(e)





if __name__ == '__main__':
    DEBUG = True
    login_url = 'https://pub.alimama.com/'
    # login_url = 'https://pub.alimama.com/promo/item/channel/index.htm?channel=nzjh'
    # 初始化一个 webdriver 对象
    device = selenium.webdriver.Chrome()
    device.maximize_window()
    device.get(login_url)
    time.sleep(5)
    device.switch_to.frame('taobaoLoginIfr')
    # 输入账号密码
    print(u'输入账号密码')

    # static_button = device.find_element_by_id('J_Static2Quick')
    static_button = device.find_element_by_id('J_Quick2Static')
    static_button.click()
    time.sleep(random.uniform(0.5, 2))
    _input_simulation(device.find_element_by_id('TPL_username_1'), '17xxxxxxxxxx')
    time.sleep(random.uniform(0.5, 2))
    # browser.find_element_by_id('TPL_password_1').send_keys('abcdefgh')
    _input_simulation(device.find_element_by_id('TPL_password_1'), 'yh86047659')
    if(_has_move(device)):
        yanzhen = device.find_element_by_id('nocaptcha')
        _move_simulation(device,yanzhen)


    pass