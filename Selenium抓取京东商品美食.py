from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from pyquery import PyQuery as pq
import time
import re

browser = webdriver.Chrome()
browser.set_window_size(1080, 720)
wait = WebDriverWait(browser, 10)


def search():
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


if __name__ == '__main__':
    main()
