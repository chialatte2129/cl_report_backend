import pytz, json
from django.db import connection, connections
from django.utils import timezone
from datetime import datetime, timedelta

# 關閉無效連線
def close_old_connections():
    for conn in connections.all():
        conn.close_if_unusable_or_obsolete()

# 時間轉換        
def timedecode(input_time):
    return input_time.strftime('%Y-%m-%d %H:%M:%S')

def timeencode(input_time, utc):
    if isinstance(input_time, str):
        input_time = datetime.strptime(input_time, '%Y-%m-%d %H:%M:%S')
    input_time += timedelta(hours=utc)
    return input_time

# 確認 Data參數
def checkDataParam(data, check_list=[]):
    status, err = True, ""
    for item in check_list:
        if status and item not in data:
            status, err = False, f"Require {item}"
            break
    return status, err

# 回覆範例
def codeStatus(code, msg=""):
    res = {'code':code, 'msg':msg, 'response_at':timedecode(timezone.now())}
    if code < 0:
        close_old_connections()
    return res

#確定時間格式，為資料庫資料添加時區

def dateTimeJsonSerialize(obj):
    if isinstance(obj, (datetime.date, datetime.datetime)):
        tp = pytz.timezone('Asia/Taipei')
        return obj.replace(tzinfo=tp).isoformat()

def dict_to_json(dictionary):
    return json.dumps(dictionary, ensure_ascii=False, indent=4, sort_keys=False)

def get_client_ip(request) -> str:
    x_forwarded_for = request.META.get("HTTP_X_REAL_IP")
    ip = x_forwarded_for.split(",")[0] if x_forwarded_for else request.META.get("REMOTE_ADDR")
    return ip

class ErrorWithCode(Exception):
    def __init__(self, code, message=""):
        self.code = code
        self.message = message
    def __str__(self):
        return repr(self.message)