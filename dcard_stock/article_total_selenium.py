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
models.create_tb(cursor, TABLES=TABLES, TBNAME=TBNAME)  # 建立 table (table存在就不建)


chromedriver = 'chromedriver.exe'
driver = webdriver.Chrome(chromedriver)
driver.get('https://www.dcard.tw/f/stock')

driver.implicitly_wait(30) # seconds

# 找到div的位置, 並將滑鼠移動到div上
x = GetSystemMetrics(SM_CXSCREEN)
y = GetSystemMetrics(SM_CYSCREEN)
driver.maximize_window()
ActionChains(driver).move_by_offset(x/2, y/2)
# 設定滑鼠滾動次數
for i in range(10000000):
    # 模擬滑鼠滾動
    win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, 0, 0, -488)
    time.sleep(0.2)
    html = driver.page_source
    soup = BeautifulSoup(html)
    a_tags = soup.find_all("a", href=re.compile("/f/stock/p/"))
    for tag in a_tags:
        tag = int(tag.get('href').split('/')[4])
        sql = "INSERT INTO `articles` (`articleID`) VALUES (%s)"
        cursor.execute(sql, (tag,))
        connect_db.commit()

connect_db.close()  # 關閉資料庫連線

# driver.quit()