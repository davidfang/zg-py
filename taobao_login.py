#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     taobao_login.py
   Description :    功能说明
   Author :       david
   date：          2018/10/12
-------------------------------------------------
   Change Activity:
                   2018/10/12:
-------------------------------------------------
"""

from selenium import webdriver
from time import sleep
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import urllib
import json
import sys

# dcap = dict(DesiredCapabilities.PHANTOMJS)
# dcap["phantomjs.page.settings.userAgent"] = (
#    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36"
# )
# driver = webdriver.PhantomJS(executable_path='/home/sevencm/phantomjs/bin/phantomjs',desired_capabilities=dcap)
# profiledir='/home/sevencm/.mozilla/firefox/miinxjat.default'
# profile=webdriver.FirefoxProfile(profiledir)
# option=webdriver.ChromeOptions()
# option.add_argument('--user-data-dir=/home/sevencm/.config/google-chrome/Default')
driver = webdriver.Chrome()
# driver.viewportSize={'width':1024,'height':800}
# driver.maximize_window()

# driver.delete_all_cookies()
driver.get(
    "https://login.taobao.com/member/login.jhtml?from=taobaoindex&f=top&style=&sub=true&redirect_url=https%3A%2F%2Fmyseller.taobao.com%2Fseller_admin.htm")
# load the switch
element = WebDriverWait(driver, 60).until(lambda driver: driver.find_element_by_xpath("//*[@id='J_Quick2Static']"))
element.click()
driver.implicitly_wait(20)
sleep(1)
username = driver.find_element_by_name("TPL_username")
if not username.is_displayed:
    driver.implicitly_wait(20)
    driver.find_element_by_xpath("//*[@id='J_Quick2Static']").click()
driver.implicitly_wait(20)
sleep(2)
username.send_keys(u'xxxx')
username.send_keys(Keys.TAB)
driver.implicitly_wait(20)
sleep(2)
pwc = driver.find_element_by_name("TPL_password")
pwc.send_keys("xxxxx")
sleep(1)
driver.save_screenshot('login-screeshot-1.png')
sleep(2)
while True:
    try:
        # 定位滑块元素,如果不存在，则跳出循环
        show = driver.find_element_by_xpath("//*[@id='nocaptcha']")
        showval = show.value_of_css_property("display")
        if not show.is_displayed():
            break
        source = driver.find_element_by_xpath("//*[@id='nc_1_n1z']")
        sleep(3)
        # 定义鼠标拖放动作
        # ActionChains(driver).drag_and_drop_by_offset(source,400,0).perform()
        # driver.save_screenshot('login-screeshot-11.png')
        action = ActionChains(driver)
        sleep(1)
        action.click_and_hold(source).perform()
        for index in range(20):
            try:
                action.move_by_offset(2, 0).perform()  # 平行移动鼠标
                driver.save_screenshot('login-screeshot-i-' + str(index) + '.png')
            except Exception as e:
                print(e)
                break
            if (index == 19):
                action.release()
                sleep(1)
                driver.save_screenshot('login-screeshot-i-' + str(index) + '.png')
            else:
                sleep(0.01)  # 等待停顿时间
                sleep(0.1)
        print(show.get_attribute("outerHTML"))
        sleep(2)
        driver.save_screenshot('login-screeshot-0.png')
        # 查看是否认证成功，获取text值 //*[@id="nc_1__scale_text"]/span
        text = driver.find_element_by_xpath("//*[@id='nc_1__scale_text']/span")
        if text.text.startswith(u'验证通过'):
            print('成功滑动')
            break
        if text.text.startswith(u'请点击'):
            print('成功滑动')
            break
        if text.text.startswith(u'请按住'):
            continue
    except Exception as e:
        print(e)
driver.find_element_by_xpath("//div[@id='nocaptcha']/div/span/a").click()
driver.find_element_by_xpath("//*[@id='J_SubmitStatic']").click()
sleep(2)
driver.save_screenshot('login-screeshot-2.png')
# 以下是获得cookie代码
cookie = [item["name"] + "=" + item["value"] for item in driver.get_cookies()]
cookiestr = ';'.join(item for item in cookie)
# print cookiestr
data = {
    'cookie': cookiestr
}
print(data)
# post cookie到接口
try:
    headers = {'Content-Type': 'application/json'}
    request = urllib.Request(url='http://127.0.0.1:8080/update/taobao/cookie', headers=headers, data=json.dumps(data))
    response = urllib.urlopen(request)
    print(response.read())
except Exception as e:
    print(e)
driver.close()
driver.quit()
sys.exit(0)

if __name__ == '__main__':
    pass
