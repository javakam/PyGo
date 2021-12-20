# https://github.com/onepureman/spider_draft
# DecryptLogin https://github.com/CharlesPikachu/DecryptLogin
# python模拟登陆淘宝（更新版） https://blog.csdn.net/tao15716645708/article/details/98870266

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

browser = webdriver.Chrome()
browser.get('https://www.bilibili.com')
#
# browser = webdriver.Chrome()
# browser.get('https://www.taobao.com')
#
# input_content = browser.find_element(By.ID,'q') #淘宝输入框<input id='q' name='q' .../>
# input_content.send_keys('iPhone')
# time.sleep(2)
# input_content.clear()
# input_content.send_keys('iPad')
# button = browser.find_element(By.CLASS_NAME,'btn-search')
# button.click()
