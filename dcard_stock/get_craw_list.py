# 此為將須爬取目標存成待工作清單的測試檔案
import config
import models
import queue

# db var
DBHOST = config.DBHOST
DBUSER = config.DBUSER
DBPASSWORD = config.DBPASSWORD
DBNAME = config.DBNAME
TABLES = config.TABLES
TBNAME_1 = config.TBNAME_1
TBNAME_2 = config.TBNAME_2

# db initialize
connect_db = models.connect_db(DBHOST, DBUSER, DBPASSWORD, db_name=DBNAME)  # mysql 連線
cursor = connect_db.cursor()  # 建立鼠標


sql = "SELECT `articleID` FROM `distinctid_articles` ORDER BY `ID` DESC"
cursor.execute(sql)
article_list = [row[0] for row in cursor.fetchall()]
# connect_db.close()
article_list_rest = article_list[7366:]
print(len(article_list))
print(article_list_rest)
# count = 11 開始

# 開啟工作實例
job_queue = queue.Queue()

# 將需工作的名單一一存進隊列
for article in article_list_rest:
    job_queue.put(article)

# 記得用 qsize() 得到隊列剩餘工作量， 重要：while 內只能有一個 .get() 不然會被取出兩次... 慘痛經驗
count = 1
while job_queue.qsize() > 0:
    post_id = str(job_queue.get())
    print(f'No.{count} id:{post_id}')
    post_url = 'https://www.dcard.tw/f/stock/p/' + post_id




