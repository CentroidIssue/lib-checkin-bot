import requests
import json
import datetime
import config
import os
import re
from datetime import datetime
import pytz
singapore_tz = pytz.timezone('Asia/Singapore')
# API Key của bạn từ cron-job.org

# URL API của cron-job.org để tạo cron job
url = "https://api.cron-job.org"
api_key = config.CRON_JOB_API_KEY

headers = {
    'Content-Type': 'application/json',
    'Authorization': f"Bearer {api_key}"
}
#print(api_key)
class JobAuth:
    enabled: bool
    user: str
    password: str

    def __init__(self, enabled: bool = 0, user: str = "", password: str = ""):
        self.enabled = enabled
        self.user = user
        self.password = password

    def eval(self):
        return {"enable": self.enabled, "user": self.user, "password": self.password}

    def __str__(self):
        return json.dumps(self.eval())


class JobNotificationSettings:
    onFailure: bool
    onSuccess: bool
    onDisable: bool

    def __init__(self, onFailure: bool, onSuccess: bool, onDisable: bool):
        self.onFailure = onFailure
        self.onSuccess = onSuccess
        self.onDisable = onDisable

    def eval(self):
        return {
            "onFailure": self.onFailure,
            "onSuccess": self.onSuccess,
            "onDisable": self.onDisable,
        }

    def __str__(self):
        return json.dumps(self.eval())


class JobExtendedData:
    headers: dict
    body: str

    def __init__(self, headers: dict, body: str):
        self.headers = headers
        self.body = body

    def eval(self):
        return {"headers": self.headers, "body": self.body}

    def __str__(self):
        return json.dumps(self.eval())

class JobStatus: int

class JobSchedule:
    timezone: str 
    expireAt: int | None
    hours: list | None
    mdays: list | None
    minutes: list | None
    months: list | None
    wdays: list | None

    def __init__(self, timezone: str = None, expireAt: int = None, hours: list = [-1], mdays: list = [-1], minutes: list = [-1], months: list = [-1], wdays: list = [-1]):
        self.timezone = timezone
        self.expireAt = expireAt
        self.hours = hours
        self.mdays = mdays
        self.minutes = minutes
        self.months = months
        self.wdays = wdays
        
    def eval(self):
        return {
            "timezone": self.timezone,
            "expireAt": self.expireAt,
            "hours": self.hours,
            "mdays": self.mdays,
            "minutes": self.minutes,
            "months": self.months,
            "wdays": self.wdays,
        }

schedule = JobSchedule(timezone="Asia/Singapore")
class JobType: int

class RequestMethod:
    GET = 0
    POST = 1
    OPTIONS = 2
    HEAD = 3
    PUT = 4
    DELETE = 5
    TRACE = 6
    CONNECT = 7
    PATCH = 8
    

class Job:
    jobId: int | None
    enabled: bool | None
    title: str | None
    saveResponses: bool | None
    url: str | None
    lastStatus: JobStatus | None
    lastDuration: int | None
    lastExecution: int | None
    nextExecution: int | None
    type: JobType | None
    requestTimeout: int | None
    redirectSuccess: bool | None
    folderId: int | None
    schedule: JobSchedule | None
    requestMethod: RequestMethod | None
         
    def __init__(self, url: str, jobId: int = None, enabled: bool = None, title: str = None, saveResponses: bool = None, lastStatus: JobStatus = None, lastDuration: int = None, lastExecution: int = None, nextExecution: int = None, type: JobType = None, requestTimeout: int = None, redirectSuccess: bool = None, folderId: int = None, schedule: JobSchedule = None, requestMethod: RequestMethod = None):
        self.jobId = jobId
        self.enabled = enabled
        self.title = title
        self.saveResponses = saveResponses
        self.url = url
        self.lastStatus = lastStatus
        self.lastDuration = lastDuration
        self.lastExecution = lastExecution
        self.nextExecution = nextExecution
        self.type = type
        self.requestTimeout = requestTimeout
        self.redirectSuccess = redirectSuccess
        self.folderId = folderId
        self.schedule = schedule
        self.requestMethod = requestMethod
        
    def eval(self):
        return {k: v for k, v in {
            "jobId": self.jobId,
            "enabled": self.enabled,
            "title": self.title,
            "saveResponses": self.saveResponses,
            "url": self.url,
            "lastStatus": self.lastStatus,
            "lastDuration": self.lastDuration,
            "lastExecution": self.lastExecution,
            "nextExecution": self.nextExecution,
            "type": self.type,
            "requestTimeout": self.requestTimeout,
            "redirectSuccess": self.redirectSuccess,
            "folderId": self.folderId,
            "schedule": None if self.schedule is None else self.schedule.eval(),
            "requestMethod": self.requestMethod,
        }.items() if v is not None}


class DetailedJob(Job):
    auth: JobAuth | None
    notification: JobNotificationSettings | None
    extendedData: JobExtendedData | None

    def __init__(
        self,
        url: str,
        auth: JobAuth = None,
        notification: JobNotificationSettings = None,
        extendedData: JobExtendedData = None,
        schedule: JobSchedule = None,
        **kwargs    
    ):
        super().__init__(url, schedule=schedule or JobSchedule(), **kwargs)  # Khởi tạo schedule mặc định nếu không có
        self.auth = auth
        self.notification = notification
        self.extendedData = extendedData
        

    def eval(self):
        return {k: v for k, v in {
            **super().eval(),
            "auth": None if self.auth is None else self.auth.eval(),
            "notification": None if self.notification is None else self.notification.eval(),
            "extendedData": None if self.extendedData is None else self.extendedData.eval(),
        }.items() if v is not None}

    def __str__(self):
        return json.dumps(self.eval())





def bubu(text: str,res: str):
    #res="Unable to Check In for this booking until 2:55pm (booking starts at 3:00pm)."
# Biểu thức chính quy để tách giờ, ngày trong tuần, tháng, ngày trong tháng và năm
    payload: DetailedJob = DetailedJob(
        url="https://libcalendar.ntu.edu.sg/r/checkin",
        extendedData=JobExtendedData(
            headers={
                "referer": "https://libcalendar.ntu.edu.sg/r/checkin",
            },
            body=json.dumps({"code": text}),
        ),
    )
    payload.eval()
    payload.requestMethod = RequestMethod.POST
    payload.schedule.timezone='Asia/Singapore'
    payload.title="check"
    payload.enabled=True
    pattern = r"until (\d{1,2}:\d{2}[ap]m) ([A-Za-z]+), ([A-Za-z]+ \d{1,2}, \d{4})"
    match = re.search(pattern, res)
    if match:
        time_str = match.group(1)  # "9:10am"
        weekday_str = match.group(2)  # "Tuesday"
        date_str = match.group(3)  # "October 29, 2024"
        # Chuyển đổi thời gian và ngày sang đối tượng datetime
        booking_datetime = datetime.strptime(f"{date_str} {time_str}", "%B %d, %Y %I:%M%p")
        # Tách ra từng thành phần
        hour = booking_datetime.hour
        minute = booking_datetime.minute
        day = booking_datetime.day
        month = booking_datetime.month
        year = booking_datetime.year
        weekday = booking_datetime.strftime("%A")  # Lấy ngày trong tuần dạng chữ
        # Chuyển đổi tên tháng sang số tháng
        # Chuyển đổi ngày trong tuần sang số cronjob (0 = Chủ Nhật, 6 = Thứ Bảy)
        day_to_number = {
            "Sunday": 0, "Monday": 1, "Tuesday": 2, "Wednesday": 3,
            "Thursday": 4, "Friday": 5, "Saturday": 6
        }
        day_of_week_number = day_to_number.get(weekday, "*")
        # Tạo cấu hình cronjob
        minute += 5
        if(minute >= 60):
            minute -= 60
            hour += 1
        payload.schedule.minutes=[minute]
        payload.schedule.hours=[hour]
        payload.schedule.months=[month]
        payload.schedule.wdays=[day_of_week_number]
        payload.schedule.mdays=[day]
    else:
        pattern = r"until (\d{1,2}:\d{2}[ap]m).*?(\d{1,2}:\d{2}[ap]m)"
        # Sử dụng regex để tìm các thời gian
        match = re.search(pattern, res)
        if match:
            check_in_time = match.group(2)
            check_in_datetime = datetime.strptime(check_in_time, "%I:%M%p")
            check_in_hour = check_in_datetime.hour
            check_in_minute = check_in_datetime.minute
            now = datetime.now(singapore_tz)
            day_of_month = now.day
            month = now.month
            day_of_week = now.weekday()  
            payload.schedule.minutes=[check_in_minute]
            payload.schedule.hours=[check_in_hour]
            payload.schedule.months=[month]
            payload.schedule.wdays=[(day_of_week+1)%7]
            payload.schedule.mdays=[day_of_month]
            print(day_of_month)

        else:
            print("Không tìm thấy thông tin thời gian phù hợp trong chuỗi.")
    print(payload.eval())
    response = requests.put(url + "/jobs", json={"job": payload.eval()}, headers=headers)

#bubu(text="6tuj",res="Unable to Check In for this booking until 8:55am Saturday, November 2, 2024 (booking starts at 9:00am Saturday, November 2, 2024).")