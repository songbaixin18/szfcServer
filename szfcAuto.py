import os
import stat
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--headless')
options.add_argument('--disable-gpu')

path = r'C:/chromedriver'
path = r'/usr/local/driver/chromedriver'


def download(url, pngName):
    # 设置chrome驱动的路径及参数
    browser = webdriver.Chrome(
        executable_path=path, options=options)
    # 获取网页内容
    browser.get(url)
    # 通过执行脚本，设置滚动条到最大宽度及最大高度
    height = browser.execute_script(
        "return document.documentElement.scrollHeight")
    browser.set_window_size(1920, height)
    # 点击 - 查询
    browser.find_element_by_id("search").click()
    time.sleep(480)
    # 点击 - 存储
    browser.find_element_by_id("save").click()
    time.sleep(60)
    # 点击 - 对比
    browser.find_element_by_id("compare").click()
    time.sleep(60)
    # 通过执行脚本，设置滚动条到最大宽度及最大高度
    height = browser.execute_script(
        "return document.documentElement.scrollHeight")
    browser.set_window_size(1920, height)
    # 保存的截图名字
    browser.save_screenshot(pngName)
    os.chmod(pngName, stat.S_IRWXU + stat.S_IRWXG + stat.S_IRWXO)
    browser.close()
    browser.quit()


if __name__ == '__main__':
    url = 'http://39.98.124.42:11580/'
    pngPath = '../data/'
    pngName = pngPath + time.strftime("%-Y-%-m-%-d", time.localtime()) + ".png"
    download(url, pngName)
