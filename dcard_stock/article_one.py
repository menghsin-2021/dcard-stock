import requests
from bs4 import BeautifulSoup
from pprint import pprint
import json


post_id = '236659514'

post_url = 'https://www.dcard.tw/f/stock/p/' + post_id
r = requests.get(post_url)
if r.status_code != requests.codes.ok:
      raise SystemExit # 結束程式

soup = BeautifulSoup(r.text, 'html.parser')

# 關鍵資訊以JSON形式存於這個script tag，因此抓取
script = soup.find('script', id='__NEXT_DATA__')
d = json.loads(script.string) # 把取出的JSON形式字串轉換回字典以方便操作
# pprint(d) # 建議先執行此行，看看整個資料結構總共有哪些東西 (底下圖1為輸出範例的區域截圖)

post_data = d['props']['initialState']['post']['data'][post_id] # 這是文章資訊在所有資料中的位置
pprint(post_data['authorName']['message']) # 作者
pprint(post_data['createdAt']) # 建立時間
pprint(post_data['content']) # 文章內容
pprint(post_data['reactionCount']) # 心情數 
pprint(post_data['commentCount']) # 留言數


# ############### 開始爬取留言 #####################

# 先取得留言數
comment_count = d['props']['initialState']['post']['data'][post_id]['commentCount']

success = 0 # debug 檢查使用
for i in range(1, comment_count+1):
      comment_url = post_url + '/b/' + str(i)
      r = requests.get(post_url)
      if r.status_code != requests.codes.ok:
            continue # 如存取不順，跳過

      soup = BeautifulSoup(r.text, 'html.parser')
      script = soup.find('script', id='__NEXT_DATA__')
      d = json.loads(script.string)

      comment_id = post_id + '-' + str(i)
      comment_data = d['props']['initialState']['comment']['data'][comment_id]
      # pprint(comment_data) # 可先執行這行了解每則留言有哪些資料訊息 (請見底下圖2為範例)

      author = comment_data['authorName']['message']
      print(author)

      # 如果是被刪除的留言 author 會變成一個清單
      if isinstance(author, list):
            print('遇到被刪除的留言 跳過就好 否則會存取不到like_count等其他資訊 會出錯')
            continue

      created_at = comment_data['createdAt']
      like_count = comment_data['likeCount']
      content = comment_data['content'] 
      print(created_at)
      print(like_count)
      print(content)
      success +=1

print('success = ', success)  # debug 檢查總共拿了幾個留言，看跟上面取到的留言數一不一樣
