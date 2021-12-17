import re
import requests
import lxml
from bs4 import BeautifulSoup
from requests.exceptions import RequestException

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains

from PIL import Image, ImageGrab
from io import BytesIO
import time


def get_one_page(url, headers):
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.text
        else:
            print(response.status_code, response.headers)
            return None
    except RequestException:
        return None


def parse_one_page(html):
    # print(html)
    soup = BeautifulSoup(html, 'lxml')
    html_ = soup.find('div', class_='main')
    # print(str(html_))
    pattern = re.compile('<dd.*?board-index.*?(\d*)</i>.*?<a.*?href="(.*?)".*?>.*?board-img.*?src="(.*?)".*?'
                         'name.*?title="(.*?)".*?star.*?>(.*?)</p>.*?releasetime.*?>(.*?)</p>.*?'
                         'integer.*?>(.*?)</i>.*?fraction.*?>(.*?)</i>.*?</dd>', re.S)
    items = re.findall(pattern, str(html_))
    print(len(items))
    for r in items:
        index, url, cover, title, star, releasetime, integer, fraction = r  # releasetime 上映时间
        url = f"https://www.maoyan.com{url}"
        score = f"{integer}{fraction}"
        star = re.sub('\s', '', star)
        releasetime = re.sub('\s', '', releasetime)
        print(index, url, cover, title, star, releasetime, score)


def handle_track(self):
    # 获取图
    driver = webdriver.Chrome()
    img = driver.find_element(By.XPATH, '/html/body/div[10]/div[2]/div[2]/div[1]/div[2]/div[1]')
    time.sleep(0.5)
    location = img.location
    size = img.size
    top, bottom, left, right = location['y'], location['y'] + size['height'], location['x'], location['x'] + size[
        'width']
    # 截取第一张图片(无缺口的)
    screenshot = driver.get_screenshot_as_png()
    screenshot = Image.open(BytesIO(screenshot))
    captcha1 = screenshot.crop((left, top, right, bottom))
    print('--->', captcha1.size)
    captcha1.save('captcha1.png')

    # 获取第二张图，先点击
    driver.find_element(By.XPATH, '/html/body/div[10]/div[2]/div[2]/div[2]/div[2]').click()
    time.sleep(2)
    img1 = driver.find_element(By.XPATH, '/html/body/div[10]/div[2]/div[2]/div[1]/div[2]/div[1]')
    time.sleep(0.5)
    location1 = img1.location
    size1 = img1.size
    top1, bottom1, left1, right1 = location1['y'], location1['y'] + size1['height'], location1['x'], location1['x'] + \
                                   size1['width']
    screenshot = driver.get_screenshot_as_png()
    screenshot = Image.open(BytesIO(screenshot))
    captcha2 = screenshot.crop((left1, top1, right1, bottom1))
    captcha2.save('captcha2.png')

    # 获取偏移量
    left = 55  # 这个是去掉开始的一部分
    for i in range(left, captcha1.size[0]):
        for j in range(captcha1.size[1]):
            # 判断两个像素点是否相同
            pixel1 = captcha1.load()[i, j]
            pixel2 = captcha2.load()[i, j]
            threshold = 60
            if abs(pixel1[0] - pixel2[0]) < threshold and abs(pixel1[1] - pixel2[1]) < threshold and abs(
                    pixel1[2] - pixel2[2]) < threshold:
                pass
            else:
                left = i
    print('缺口位置', left)

    time.sleep(3)

    left -= 54
    # 开始移动
    track = self.get_track(left)

    print('滑动轨迹', track)
    track += [5, -5]  # 滑过去再滑过来，不然有可能被吃
    # 拖动滑块
    starttime = time.time()
    slider = driver.find_element(By.XPATH, '/html/body/div[10]/div[2]/div[2]/div[2]/div[2]')
    ActionChains(driver).click_and_hold(slider).perform()
    for x in track:
        ActionChains(driver).move_by_offset(xoffset=x, yoffset=0).perform()
    ActionChains(driver).release().perform()

    endtime = time.time()
    print("时间：")
    print(endtime - starttime)
    time.sleep(1)
    try:
        if driver.find_element(By.XPATH, '/html/body/div[10]/div[2]/div[2]/div[2]/div[2]'):
            print('能找到滑块，重新试')
            driver.delete_all_cookies()
            driver.refresh()
            # self.autologin(text_login, text_password)  # 重新登陆
        else:
            print('login success')
    except:
        print('login success')
    time.sleep(2)

    return driver


'''
@description: 滑块位移的计算
@param {type} 
@return: 
'''


def get_track(self, distance):
    """
    根据偏移量获取移动轨迹
    :param distance: 偏移量
    :return: 移动轨迹
    """
    # 移动轨迹
    track = []
    # 当前位移
    current = 0
    # 减速阈值
    mid = distance * 2 / 5
    # 计算间隔
    t = 0.2
    # 初速度
    v = 1

    while current < distance:
        if current < mid:
            # 加速度为正2
            a = 3.1
        else:
            # 加速度为负3
            a = -3
            # 初速度v0
        v0 = v
        # 当前速度v = v0 + at
        v = v0 + a * t
        # 移动距离x = v0t + 1/2 * a * t^2
        move = v0 * t + 1 / 2 * a * t * t
        # 当前位移
        current += move
        # 加入轨迹
        track.append(round(move))
    return track


def main():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:76.0) Gecko/20100101 Firefox/76.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        "Connection": "close"
    }
    url = 'https://maoyan.com/board/4'
    html = get_one_page(url, headers)
    parse_one_page(html)


if __name__ == '__main__':
    main()
