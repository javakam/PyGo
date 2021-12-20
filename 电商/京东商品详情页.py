from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By


def getData(driver, keyword):
    try:
        return (driver.find_element(By.XPATH, "//li[contains(text(),'" + keyword + "')]").text)
    except:
        return ('fail')


def getPrice(driver):
    try:
        temp = driver.find_element(By.XPATH,
                                   '/html/body/div[6]/div/div[2]/div[4]/div/div[1]/div[2]/span[1]/span[2]').text
        return temp
    except NoSuchElementException:
        temp = driver.find_element(By.XPATH,
                                   '/html/body/div[6]/div/div[2]/div[3]/div/div[1]/div[2]/span[1]/span[2]').text
        return temp
    except:
        return ('fail')


def spider(driver, link, needlist):
    driver.get(link)
    temp = []
    try:
        element = driver.find_element(By.CLASS_NAME, 'p-parameter')
    except:
        temp = [['fail'] * len(needlist) for x in range(len(needlist))]
    else:
        for i in needlist:
            temp.append(getData(driver, i))

    # 如果想要价格信息开启
    temp.append(getPrice(driver))

    temp.append(link)
    return temp


###########################  用例

# import jdSpider
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.common.action_chains import ActionChains
from selenium import webdriver

# 如果重复开启driver会很慢，因此先开启然后将driver传入函数中
options = webdriver.ChromeOptions()
# options.add_argument('--headless')  #开启无头模式
# 更改chromedriver.exe路径
driver = webdriver.Chrome(options=options)  # executable_path = 'D:\chromedriver.exe',
driver.maximize_window()

url = 'https://item.jd.com/11062841516.html'
needlist = ['商品名称', '商品编号', '商品产地', '制作口味', '适用场景']
result = spider(driver, url, needlist)

print(result)
