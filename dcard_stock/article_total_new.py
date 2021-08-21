import pandas as pd
import requests
from sqlalchemy import create_engine
import time
import cloudscraper


import models
import config

# db var
DBHOST = config.DBHOST
DBUSER = config.DBUSER
DBPASSWORD = config.DBPASSWORD
DBNAME = config.DBNAME
TABLES = config.TABLES
TBNAME = config.TBNAME

# crawler
# 股版依時間順序前100則文章url
url = 'https://www.dcard.tw/service/api/v2/forums/stock/posts?limit=100'

# 輸入 json 資料中一筆字典並建立 dataFrame
def dj_to_df(dj):
    df = pd.DataFrame(data=
                      [{'articleID': dj['id'],  # 編號
                        'title': dj['title'],  # 標題
                        'createdAt': pd.Timestamp(dj['createdAt'], tz='Asia/Taipei'),  # 發布時間
                        'updatedAt': pd.Timestamp(dj['updatedAt'], tz='Asia/Taipei'),  # 更新時間
                        'commentCount': dj['commentCount'],  # 留言數
                        'forumName': dj['forumName'],  # 論壇分類(中文)
                        'forumAlias': dj['forumAlias'],  # 論壇分類(英文)
                        'likeCount': dj['likeCount'],  # 心情數量
                        'topics': "/".join(dj['topics'])}],  # 標籤
                      columns=['articleID', 'title', 'createdAt', 'updatedAt', 'commentCount',
                               'forumName', 'forumAlias', 'likeCount', 'topics'],
                      )
    return df


# 透過request套件抓下網址資料，並存成 dataframe
def crawl(url):
    df = pd.DataFrame(columns=['articleID', 'title', 'createdAt', 'updatedAt', 'commentCount',
                               'forumName', 'forumAlias', 'likeCount', 'topics'])

    r = requests.get(url)
    if r.status_code != requests.codes.ok:
        print(r.status_code)
        scraper = cloudscraper.create_scraper()  # returns a CloudScraper instance
        r = scraper.get(url)

    for i in range(len(r.json())):
        dj = r.json()[i]
        df = df.append(dj_to_df(dj), ignore_index=True)

    return df

# 將整個 dataframe 存入 (這裡只能用 sqlalchemy)
def df_row_insert(data):
    engine = create_engine("mysql+pymysql://{user}:{pw}@localhost/{db}"
                           .format(user=DBUSER,
                                   pw=DBPASSWORD,
                                   db=DBNAME))
    data.to_sql('articles', con=engine, if_exists='append', chunksize=1000, index=False)
    # articles is the name of table into which we want to insert our DataFrame
    # con = engine provides the connection details (recall that we created engine using our authentication details in the previous step)
    # if_exists = 'append'checks whether the table we specified already exists or not, and then appends the new data (if it does exist) or creates a new table (if it doesn’t).
    # chunksize writes records in batches of a given size at a time. By default, all rows will be written at once.

# db initialize
connect_db = models.connect_db(DBHOST, DBUSER, DBPASSWORD)  # mysql 連線
cursor = connect_db.cursor()  # 建立鼠標
cursor = models.create_db(cursor, DBNAME=DBNAME)  # 建立新資料庫(資料庫存在就不建)
models.create_tb(cursor, TABLES=TABLES, TBNAME_1=TBNAME)  # 建立 table (table存在就不建)
connect_db.close()  # 關閉資料庫連線

# 先存第一筆資料
data = crawl(url)

# 利用第一筆資料找到末筆資料
count = 100

# 一次循環100篇
for i in range(10):
    try:
        last = str(int(data.tail(1).articleID))  # 找出爬出資料的最後一筆ID
        after_url = 'https://www.dcard.tw/service/api/v2/forums/stock/posts?limit=100&before=' + last
        data = data.append(crawl(after_url), ignore_index=True)
        count += 100
        print(count)
        time.sleep(10)
    except:
        print('finish')
        break

# 存入資料庫
df_row_insert(data)