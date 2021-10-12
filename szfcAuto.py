import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')

path = r'C:/chromedriver'


def download(url, pngName):
    # 设置chrome驱动的路径及参数
    browser = webdriver.Chrome(
        executable_path=path, chrome_options=chrome_options)
    # 获取网页内容
    browser.get(url)
    # 通过执行脚本，设置滚动条到最大宽度及最大高度
    height = browser.execute_script(
        "return document.documentElement.scrollHeight")
    browser.set_window_size(1920, height)
    # 点击 - 查询
    browser.find_element_by_id("search").click()
    time.sleep(180)
    # 点击 - 存储
    browser.find_element_by_id("save").click()
    time.sleep(60)
    # 点击 - 对比
    browser.find_element_by_id("save").click()
    time.sleep(60)
    # 通过执行脚本，设置滚动条到最大宽度及最大高度
    height = browser.execute_script(
        "return document.documentElement.scrollHeight")
    browser.set_window_size(1920, height)
    # 保存的截图名字
    browser.save_screenshot(pngName)
    browser.quit()


if __name__ == '__main__':
    url = 'http://47.92.100.56:11580/'
    pngPath = '../data/'
    pngName = pngPath + time.strftime("%Y-%m-%d", time.localtime()) + ".png"
    download(url, pngName)
