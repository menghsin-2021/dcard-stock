import json
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import queue

import config
import models

# db var
DBHOST = config.DBHOST
DBUSER = config.DBUSER
DBPASSWORD = config.DBPASSWORD
DBNAME = config.DBNAME
TABLES = config.TABLES
TBNAME_1 = config.TBNAME_1
TBNAME_2 = config.TBNAME_2

# db initialize
connect_db = models.connect_db(DBHOST, DBUSER, DBPASSWORD)  # mysql 連線
cursor = connect_db.cursor()  # 建立鼠標
cursor = models.create_db(cursor, DBNAME=DBNAME)  # 建立新資料庫(資料庫存在就不建)
models.create_tb(cursor, TABLES=TABLES, TBNAME_1=TBNAME_1, TBNAME_2=TBNAME_2)  # 建立 table (table存在就不建)

# # ############### 開始爬取作者貼文 #####################

sql = "SELECT `articleID` FROM `distinctid_articles` ORDER BY `ID` DESC"
cursor.execute(sql)
article_list = [row[0] for row in cursor.fetchall()]
# connect_db.close()
article_list_rest = article_list[4552:]
job_queue = queue.Queue()

for article in article_list_rest:
    job_queue.put(article)

count = 4553
while job_queue.qsize() > 0:
    post_id = str(job_queue.get())
    print(f'No.{count} id:{post_id}')
    post_url = 'https://www.dcard.tw/f/stock/p/' + post_id

    r = requests.get(post_url)
    if r.status_code != requests.codes.ok:
        raise SystemExit  # 結束程式

    soup = BeautifulSoup(r.text, 'html.parser')

    # 關鍵資訊以JSON形式存於這個script tag，因此抓取
    script = soup.find('script', id='__NEXT_DATA__')
    d = json.loads(script.string)  # 把取出的JSON形式字串轉換回字典以方便操作
    # pprint(d) # 建議先執行此行，看看整個資料結構總共有哪些東西 (底下圖1為輸出範例的區域截圖)

    post_data = d['props']['initialState']['post']['data'][post_id]  # 這是文章資訊在所有資料中的位置

    if not post_data['school']:  # 如果作者存在
        print('遇到被刪除的貼文 跳過就好 否則會存取不到like_count等其他資訊 會出錯')
        # continue  # 省略下半部

    articleID = post_data['id']  # 貼文 id
    author = post_data['school']  # 作者
    forum_alias = post_data['forumAlias']  # 論壇名稱
    created_at_utc = datetime.fromisoformat(
        post_data['createdAt'].split('Z')[0])  # type datetime.datetime 建立時間 (2021-08-06 09:54:46.599000) 取出來記得時區+8
    created_at_tw = created_at_utc + timedelta(hours=+8)  # type datetime.datetime 建立時間 (2021-08-06 17:54:46.599000)
    time_string = post_data['timeString']  # 時間字串
    title = post_data['title']  # 文章標題
    topics = '/'.join([str(topic) for topic in post_data['topics']])  # 文章主題
    content = post_data['content']  # 文章內容
    gender = post_data["gender"]  # 作者性別
    react_count = post_data['reactionCount']  # 心情數 = like_count
    comment_count = post_data['commentCount']  # 留言數

    sql = "INSERT INTO `posts` (`articleID`, `author`, `forum_alias`, `created_at_utc`, `created_at_tw`, `time_string`, `title`, `topics`, `content`, `gender`, `react_count`, `comment_count`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    # cursor.execute("SET time_zone = '+08:00'")  # UTC+8為台灣區的時間
    # 如果SQL的time_zone沒有特別設定，則所有日期和時間值都是來自執行SQL Server其電腦的作業系統。
    cursor.execute(sql, (
    articleID, author, forum_alias, created_at_utc, created_at_tw, time_string, title, topics, content, gender, react_count,
    comment_count))
    connect_db.commit()

    # connect_db.close()  # 關閉資料庫連線

    # # ############### 開始爬取留言 #####################

    # 先取得留言數
    comment_count = d['props']['initialState']['post']['data'][post_id]['commentCount']
    print(f'total comment count = {comment_count}')

    success = 0  # debug 檢查使用
    for i in range(1, comment_count + 1):
        comment_url = post_url + '/b/' + str(i)
        r = requests.get(comment_url)
        if r.status_code != requests.codes.ok:
            continue  # 如存取不順，跳過

        soup = BeautifulSoup(r.text, 'html.parser')
        script = soup.find('script', id='__NEXT_DATA__')
        d = json.loads(script.string)

        reaction_id = post_id + '-' + str(i)
        comment_id = d['props']['initialState']['comment']['doorplateMap'][reaction_id]
        comment_data = d['props']['initialState']['comment']['data'][comment_id]
        # pprint(comment_data) # 可先執行這行了解每則留言有哪些資料訊息

        try:
            author = comment_data['school']
        except:
            print('遇到被刪除的留言 跳過就好 否則會存取不到like_count等其他資訊 會出錯')
            continue  # 省略下半部

        reactionID = reaction_id
        articleID = comment_data['postId']
        created_at_utc = datetime.fromisoformat(comment_data['createdAt'].split('Z')[0])
        created_at_tw = created_at_utc + timedelta(hours=+8)
        like_count = comment_data['likeCount']
        content = comment_data['content']

        sql = "INSERT INTO `reactions` (`reactionID`, `articleID`, `author`, `created_at_utc`, `created_at_tw`, `content`, `like_count`) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        # cursor.execute("SET time_zone = '+08:00'")  # UTC+8為台灣區的時間
        # 如果SQL的time_zone沒有特別設定，則所有日期和時間值都是來自執行SQL Server其電腦的作業系統。
        cursor.execute(sql, (reactionID, articleID, author, created_at_utc, created_at_tw, content, like_count))
        connect_db.commit()
        success += 1

    print('success = ', success)  # debug 檢查總共拿了幾個留言，看跟上面取到的留言數一不一樣
    count += 1
connect_db.close()  # 關閉資料庫連線