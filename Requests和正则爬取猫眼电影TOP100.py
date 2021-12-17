import json
import re
import requests
from time import time
from multiprocessing import Pool
from bs4 import BeautifulSoup
from requests.exceptions import RequestException


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
        # index, url, cover, title, actor, releasetime, integer, fraction = r  # releasetime 上映时间
        # url = f"https://www.maoyan.com{url}"
        # score = f"{integer}{fraction}"
        # actor = re.sub('\s', '', actor)
        # releasetime = re.sub('\s', '', releasetime)
        # print(index, url, cover, title, star, releasetime, score)

        # 或者
        yield {
            'index': r[0],
            'title': r[3],
            'actor': r[4].strip()[3:],  # "主演：徐峥" 👉 "徐峥"
            'releasetime': r[5].strip()[5:],  # 同理: 上映时间：2020-01-03 9.3 👉 2020-01-03 9.3
            'score': r[6] + r[7],
            'url': f"https://www.maoyan.com{r[1]}",
            'cover': r[2]
        }


def write_to_file(content):
    # 'a' 表示追加
    with open('result_maoyan.txt', 'a', encoding='utf8') as f:
        f.write(json.dumps(content, ensure_ascii=False) + '\n')
        f.close()


def main(offset):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:76.0) Gecko/20100101 Firefox/76.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        "Connection": "close"
    }
    url = f'https://maoyan.com/board/4?offset={offset}'
    html = get_one_page(url, headers)
    for item in parse_one_page(html):
        print(item)
        write_to_file(item)


if __name__ == '__main__':
    # 猫眼 TOP100 共 10页数据每页十条
    start = time()

    # 耗时：2.844808340072632秒
    # for i in range(10):
    #     main(i * 10)

    # 耗时：1.3851382732391357秒
    pool = Pool()
    pool.map(main, [i * 10 for i in range(10)])

    end = time()
    print("耗时：" + str(end - start) + "秒")
