from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from pyquery import PyQuery as pq
import time
import re
# 目标站点: https://www.jd.com
#
from config_jd import *
import pymongo
client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]

# 使用 Chrome 或 Firefox 的无头版替代 PhantomJS
# 这段代码定义了headless chrome，所有的配置都一样
# 用Python做爬虫的各位，不要再用PhantomJS了 👉 https://www.jianshu.com/p/31f2b63437ed
options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1366x768')

user_agent = (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_4) " +
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.57 Safari/537.36"
)

# 通过设置user-agent，用来模拟移动设备 -> 会进入 m.jd.com
# user_agent = 'MQQBrowser/26 Mozilla/5.0 (Linux; U; Android 2.3.7; zh-cn; MB200 Build/GRJ22; ' \
#              'CyanogenMod-7) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1'
# options.add_argument('--user-agent=iphone')

options.add_argument('user-agent=%s' % user_agent)

# 1. Chrome
browser = webdriver.Chrome(options=options)
# 2. PhantomJS
# browser = webdriver.PhantomJS(service_args=SERVICE_ARGS)
# browser.set_window_size(1400, 900)
wait = WebDriverWait(browser, 10)


def search():
    print('正在搜索')
    try:
        browser.get('https://www.jd.com')
        content = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#key"))
        )
        submit = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#search > div > div.form > button')))
        content.send_keys('美食')
        submit.click()

        # 直接获取"共100页"的"100"标签, 这里为了练习正则表达式, 采用另外一种方法.
        total = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#J_bottomPage > span.p-skip > em:nth-child(1) > b"))
        )
        # 返回 "共100页  到第" , 使用正则提取出100
        # total = wait.until(
        #     EC.presence_of_element_located((By.CSS_SELECTOR, "#J_bottomPage > span.p-skip > em:nth-child(1)"))
        # )
        return total.text
    except TimeoutException:
        search()


def next_page(page_number):
    print('正在翻页', page_number)
    try:
        input_page = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#J_bottomPage > span.p-skip > input"))
        )
        confirm = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#J_bottomPage > span.p-skip > a')))
        input_page.clear()
        input_page.send_keys(page_number)
        confirm.click()
        wait.until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, '#J_bottomPage > span.p-num > a.curr'),
                                             str(page_number))
        )
        print(f"当前页码:{page_number}")
        get_products()  # wait.until(get_products())
    except TimeoutException:
        print(f"超时重试:{page_number}")
        next_page(page_number)


# todo 2021年12月17日 17:03:16  image 懒加载导致为None
# todo 保存至 mongo https://www.bilibili.com/video/BV1434y1U7B9?p=16&t=1902.1
def get_products():
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#J_goodsList ul .gl-item')))
    html = browser.page_source
    doc = pq(html)
    items = doc('#J_goodsList ul .gl-item').items()
    for item in items:
        # title = re.search(r'</span>.*?(.*?).*?</em>', title, re.S)[0]
        # title = re.sub(r'<[^>]*>', '', title)  # 去除字符串中的html标签,如<font>,<span>等
        title = item.find('.p-name em')
        title.find('span').remove()  # 去除"京东超市 "

        product = {
            'image': item.find('.p-img img').attr('src'),
            'price': item.find('.p-price strong i').text(),  # "69人购买"->"69": xxx.text()[:-3]
            'title': title.text().replace('\n', ''),
            'comments': item.find('.p-commit a').text(),  # 2万+
            'shop': item.find('.p-shop a').text()
        }
        print(product)
        save_to_mongo(product)


def save_to_mongo(result):
    try:
        if db[MONGO_TABLE].insert_one(result):
            print('保存成功', result)
    except Exception:
        print('保存失败', result)


def main():
    total = search()
    print("当前页码:1")
    get_products()

    total = int(total)
    print(total)
    # total = re.search('(\d+)', total, re.S)
    # print(int(total[1]))
    for i in range(2, total + 1):
        next_page(i)
    browser.close()


if __name__ == '__main__':
    main()
