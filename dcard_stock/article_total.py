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

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-TW,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6,ja;q=0.5",
    "Host": "httpbin.org",
    "Referer": "https://www.learncodewithmike.com/",
    "Sec-Ch-Ua": "\"Chromium\";v=\"92\", \" Not A;Brand\";v=\"99\", \"Microsoft Edge\";v=\"92\"",
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "cross-site",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36 Edg/92.0.902.73",
    "X-Amzn-Trace-Id": "Root=1-611d0869-62da9c19029753db1b1c8be1"
  }


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


# 透過request套件抓下網址資料
def crawl(url):
    df = pd.DataFrame(columns=['articleID', 'title', 'createdAt', 'updatedAt', 'commentCount',
                               'forumName', 'forumAlias', 'likeCount', 'topics'])

    r = requests.get(url, headers=headers)
    if r.status_code != requests.codes.ok:
        print(r.status_code)
        scraper = cloudscraper.create_scraper()  # returns a CloudScraper instance
        r = scraper.get(url)

    for i in range(len(r.json())):
        dj = r.json()[i]
        df = df.append(dj_to_df(dj), ignore_index=True)

    return df

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
models.create_tb(cursor, TABLES=TABLES, TBNAME=TBNAME)  # 建立 table (table存在就不建)
connect_db.close()  # 關閉資料庫連線

data = crawl(url)

count = 100
for i in range(1):
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

df_row_insert(data)