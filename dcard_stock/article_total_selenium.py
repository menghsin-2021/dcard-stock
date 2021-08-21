from selenium import webdriver
import time
from bs4 import BeautifulSoup
import re
import win32api
import win32con
from win32api import GetSystemMetrics
from win32con import SM_CXSCREEN, SM_CYSCREEN
from selenium.webdriver.common.action_chains import ActionChains

import models
import config

# db var
DBHOST = config.DBHOST
DBUSER = config.DBUSER
DBPASSWORD = config.DBPASSWORD
DBNAME = config.DBNAME
TABLES = config.TABLES
TBNAME = config.TBNAME


# db initialize
connect_db = models.connect_db(DBHOST, DBUSER, DBPASSWORD)  # mysql 連線
cursor = connect_db.cursor()  # 建立鼠標
cursor = models.create_db(cursor, DBNAME=DBNAME)  # 建立新資料庫(資料庫存在就不建)
models.create_tb(cursor, TABLES=TABLES, TBNAME_1=TBNAME)  # 建立 table (table存在就不建)

# 開啟瀏覽器模擬器
chromedriver = 'chromedriver.exe'
driver = webdriver.Chrome(chromedriver)
driver.get('https://www.dcard.tw/f/stock')

# 等待網頁載入
driver.implicitly_wait(30) # seconds

# 找到div的位置, 並將滑鼠移動到div上 (實際上自己將滑鼠移到頁面就好，中途滑鼠可短暫離開)
x = GetSystemMetrics(SM_CXSCREEN)
y = GetSystemMetrics(SM_CYSCREEN)
driver.maximize_window()
ActionChains(driver).move_by_offset(x/2, y/2)
# 設定滑鼠滾動次數
for i in range(10000000):
    # 模擬滑鼠向下滾動
    win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, 0, 0, -488)
    # 停頓 0.2 秒
    time.sleep(0.2)
    # 存下頁面
    html = driver.page_source
    soup = BeautifulSoup(html)
    # 用正規表達式找到文章ID
    a_tags = soup.find_all("a", href=re.compile("/f/stock/p/"))
    # 找到一組ID就存入資料庫
    for tag in a_tags:
        tag = int(tag.get('href').split('/')[4])
        sql = "INSERT INTO `articles` (`articleID`) VALUES (%s)"
        cursor.execute(sql, (tag,))
        connect_db.commit()

connect_db.close()  # 關閉資料庫連線

# driver.quit()