# 測試 datetime 格式 時區轉換等
from datetime import datetime, timezone, timedelta
import pytz

time_datetime = '2021-08-06T09:54:46.599Z'.split('Z')[0]  # 將字串轉成可以讓 datetime 辨認的 isoformat 時間字串
print(time_datetime)
# 2021-08-06T09:54:46.599
time_datetime = datetime.fromisoformat(time_datetime)  # 將時間字串轉成 datetime 結構
# 2021-08-06 09:54:46.599000

# 設定為 +8 時區
# tz = timezone(timedelta(hours=+8))  # 這個用時間差改時區
tz = pytz.timezone('Asia/Taipei')  # 這個用套件直接給時區

# time_datetime_tw = time_datetime.replace(tzinfo=tz)  # 這個才會真正換時區
# 2021-08-06 09:54:46.599000+08:00

# time_datetime_tw = time_datetime.astimezone(tz)  # 這個只有在後面標註時區
# 2021-08-06 09:54:46.599000+08:00

time_datetime_tw = time_datetime + timedelta(hours=+8)  # 直接用+的最快


print(time_datetime_tw)  # 2021-08-06 17:54:46.599000
print(time_datetime_tw.tzinfo)  # None

