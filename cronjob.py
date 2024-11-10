import requests
import json
from typing import Union
import datetime
import config
import os
import re
from datetime import datetime
import pytz
import traceback

singapore_tz = pytz.timezone("Asia/Singapore")

url = "https://api.cron-job.org"

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {config.CRON_JOB_API_KEY}",
}


class JobAuth:
    enabled: bool
    user: str
    password: str

    def __init__(self, enabled: bool = 0, user: str = "", password: str = ""):
        self.enabled = enabled
        self.user = user
        self.password = password

    def eval(self):
        return {
            "enable": self.enabled,
            "user": self.user,
            "password": self.password}

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


class JobStatus:
    int


class JobSchedule:
    """
    The JobSchedule object represents the execution schedule of a job

    See: https://docs.cron-job.org/rest-api.html#jobschedule

    Returns:
    """

    def __init__(
        self,
        timezone: str = None,
        expiresAt: int = None,
        hours: list = [-1],
        mdays: list = [-1],
        minutes: list = [-1],
        months: list = [-1],
        wdays: list = [-1],
    ):
        print(timezone, expiresAt, hours, mdays, minutes, months, wdays)
        self._timezone = timezone
        self._expiresAt = expiresAt
        self.hours = hours
        self.mdays = mdays
        self.minutes = minutes
        self.months = months
        self.wdays = wdays

    @property
    def timezone(self):
        """
        See: https://www.php.net/manual/en/timezones.php
        Returns:
            str: The timezone of the job
        """
        return self._timezone

    @property
    def expiresAt(self) -> int:
        """
        The time when the job expires

        The format is "YYYYMMDDhhmmss" (In timezone from the timezone property)
        Returns:
            int: The time when the job expires
        """
        return self._expiresAt

    @timezone.setter
    def timezone(self, value: str):
        self._timezone = value

    @expiresAt.setter
    def expiresAt(self, value: int):
        self._expiresAt = value

    def eval(self):
        return {
            "timezone": self.timezone,
            "expiresAt": self.expiresAt,
            "hours": self.hours,
            "mdays": self.mdays,
            "minutes": self.minutes,
            "months": self.months,
            "wdays": self.wdays,
        }


class JobType:
    int


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

    def __init__(
        self,
        url: str,
        jobId: int = None,
        enabled: bool = None,
        title: str = None,
        saveResponses: bool = None,
        lastStatus: JobStatus = None,
        lastDuration: int = None,
        lastExecution: int = None,
        nextExecution: int = None,
        type: JobType = None,
        requestTimeout: int = None,
        redirectSuccess: bool = None,
        folderId: int = None,
        schedule: JobSchedule = None,
        requestMethod: RequestMethod = None,
    ):
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
        return {
            k: v
            for k, v in {
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
            }.items()
            if v is not None
        }


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
        **kwargs,
    ):
        super().__init__(
            url, schedule=schedule or JobSchedule(), **kwargs
        )  # Khởi tạo schedule mặc định nếu không có
        self.auth = auth
        self.notification = notification
        self.extendedData = extendedData

    def eval(self):
        return {
            k: v
            for k, v in {
                **super().eval(),
                "auth": None if self.auth is None else self.auth.eval(),
                "notification": (
                    None if self.notification is None else self.notification.eval()
                ),
                "extendedData": (
                    None if self.extendedData is None else self.extendedData.eval()
                ),
            }.items()
            if v is not None
        }

    def __str__(self):
        return json.dumps(self.eval())


class Jobs:
    _jobs: dict[str, Job] = {}

    @classmethod
    def set_jobs(cls, jobs: list[Job]):
        """Set the jobs for the class

        The jobs are stored in a dictionary with the title as the key

        Args:
            jobs (list[Job]): A list of jobs class
        """

        jobs = [Job(**job) for job in jobs]
        cls._jobs = {job.title: job for job in jobs}

    @classmethod
    def add_job(cls, job: DetailedJob) -> requests.Response:
        """Add a job to the class

        Args:
            job (Job): The job to add

        Returns:
            Response: The response from the API
        """
        payload = job.eval()
        response = requests.put(f"{url}/jobs", json={"job": payload}, headers=headers)
        cls._jobs[job.title] = job
        return response

    @classmethod
    def __str__(cls):
        return json.dumps(cls._jobs)

    @classmethod
    def get_jobs(cls):
        return cls._jobs

    @classmethod
    def sync_jobs(cls) -> requests.Response:
        """Sync all cron jobs from the API
        If the response status is 200, the jobs are set to the class
        If the response status is 429, it means that a rate limit has been reached
        Returns:
            Response: The jobs from the API
        """
        response = requests.get(f"{url}/jobs", headers=headers)
        if response.status_code == 200:
            cls.set_jobs(jobs=response.json()["jobs"])
            return cls.get_jobs()
        return response


def create_cron_job(code: str, booking_time: datetime, chat_id: str) -> str:
    """Create a cron job to check in for a booking

    Args:
        code (str): The code to check in
        booking_time (datetime): The time to check in for the booking

    Returns:
        _type_: True if successful, False otherwise
    """
    try:

        payload: DetailedJob = DetailedJob(
            url=f"{config.BACKEND_URL}/checkin",
            extendedData=JobExtendedData(
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {config.CRON_JOB_API_KEY}",
                },
                body=json.dumps({"code": code, "chat_id": chat_id}),
            ),
        )
        payload.eval()
        payload.requestMethod = RequestMethod.POST
        payload.schedule.timezone = "Asia/Singapore"
        payload.title = code
        payload.enabled = True

        # Convert day of week to number
        day_to_number = {
            "Sunday": 0,
            "Monday": 1,
            "Tuesday": 2,
            "Wednesday": 3,
            "Thursday": 4,
            "Friday": 5,
            "Saturday": 6,
        }

        # Specific time
        hour = booking_time.hour
        print(hour)
        minute = booking_time.minute
        day = booking_time.day
        month = booking_time.month
        year = booking_time.year
        weekday = booking_time.strftime("%A")
        print(hour, minute, day, month, year, weekday)

        day_of_week_number = day_to_number.get(weekday, "*")

        # Ensure hour, minute, day, and month are two characters long
        hour_str = str(hour).zfill(2)
        minute_str = str(minute).zfill(2)
        day_str = str(day).zfill(2)
        month_str = str(month).zfill(2)
        payload.schedule.expiresAt = int(f"{year}{month_str}{day_str}{hour_str}{minute_str}01")
        print(payload.schedule.expiresAt)
        payload.schedule.minutes = [minute]
        payload.schedule.hours = [hour]
        payload.schedule.months = [month]
        payload.schedule.wdays = [day_of_week_number]
        payload.schedule.mdays = [day]
        response = Jobs.add_job(payload)
        print(response.text)
        print(response.status_code)
        return response.json()
    except Exception as e:
        raise e


# try:
#     response = Jobs.sync_jobs()
#     if response.status_code == 429:
#         print("Rate limit reached")
#         headers = {
#             "Content-Type": "application/json",
#             "Authorization": f"Bearer {config.CRON_JOB_API_KEY1}",
#         }
#         response = Jobs.sync_jobs()
# except Exception as e:
#     print("Error: Unable to sync jobs", e, traceback.print_exc())
# # bubu(text="6tuj",res="Unable to Check In for this booking until 8:55am Saturday, November 2, 2024 (booking starts at 9:00am Saturday, November 2, 2024).")
