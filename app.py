import requests
from flask import Flask, request

import re
import json
from bs4 import BeautifulSoup
from datetime import datetime, date, timedelta
from dataclasses import dataclass
import config
import pytz
from typing import Union, List
from telegram import *
import cronjob
import traceback

app = Flask(__name__)
singapore_tz = pytz.timezone("Asia/Singapore")

STATUS: dict[str, str] = {}


@app.route("/", methods=["GET"])
def home():
    return "Hello world"


@app.route("/webhook", methods=["POST"])
def webhook():
    """Receive API from telegram"""
    try:
        data = request.json
        print(data)

        if "message" in data:

            chat = Chat(
                data["message"]["chat"]["id"],
                data["message"]["chat"]["type"],
                data["message"]["chat"].get("title", None),
                data["message"]["chat"].get("username", None),
                data["message"]["chat"].get("first_name", None),
                data["message"]["chat"].get("last_name", None),
            )
            text: str = data["message"].get("text", "")
            user = User(
                data["message"]["from"]["id"],
                data["message"]["from"].get("is_bot", None),
                data["message"]["from"].get("first_name", None),
                data["message"]["from"].get("last_name", None),
                data["message"]["from"].get("username", None),
                data["message"]["from"].get("language_code", None),
            )
            message = Message(
                data["message"]["message_id"],
                user,
                chat,
                data["message"]["date"],
                text)

            if text.startswith("/"):
                print(f"chat_id: {chat.id}")
                print(f"text: {text}")
                handle_command(user.id, chat.id, text)

            elif user.id in STATUS and STATUS[user.id] == "code":
                print(f"Code: {text}")
                if handleCode(user.id, chat.id, text):
                    send_message(chat.id, "Code accepted ✅")
                else:
                    send_message(chat.id, "Code rejected ⛔️")
                STATUS[user.id] = "normal"
                pass

            print(message.eval())
    except Exception as e:
        print("Error:", e, traceback.format_exc())
    return "OK", 200


@app.route("/checkin", methods=["POST"])
def checkin():
    """Check in the user"""
    data = request.json
    print(data)
    code = data.get("code", None)
    if code is None:
        return "Code not found", 400
    chat_id = data.get("chat_id", None)
    if chat_id is None:
        return "Chat ID not found", 400
    handleCode("0", chat_id, code)
    return "OK", 200


def handle_command(user_id: str, chat_id: str, command: str):
    """_summary_

    Args:
        chat_id (str): _description_
        text (str): _description_
    """

    match command:
        case "/start":
            send_message(
                chat_id,
                "Welcome! I'm your bot. How can I assist you?")
        case "/help":
            send_message(
                chat_id,
                "Available commands:\n/start - Start the bot\n/help - Show this help message",
            )
        case "/pending":
            cnt = 0
        case "/code":
            send_message(chat_id, "Please enter your code")
            STATUS[user_id] = "code"


def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{config.BOT_TOKEN}/sendMessage"
    data = {"chat_id": chat_id, "text": text}
    requests.post(url, json=data)


def setWebhook(url: str) -> Union[str, dict]:
    """Set telegram webhook to point to this server

    Args:
        url (str): URL of the server

    Returns:
        Union[str, dict]: Response from the API, either error message or success message
    """
    try:
        url = f"https://api.telegram.org/bot{config.BOT_TOKEN}/setWebhook?url={url}/webhook"
        print(url)
        response = requests.get(url)
        return response.json()
    except Exception as e:
        raise e


def handleCode(user_id: str, chat_id: str, code: str) -> bool:
    """Handle the checkin code from the user

    Args:
        user_id (str): ID of the user
        chat_id (str): ID of the chat
        code (str): Code from user

    Returns:
        bool: True if the code is valid, False otherwise
    """

    try:
        response = sendCode(code).text
        print("Response:", response)
        if response == "Unable to find booking matching code":
            send_message(chat_id, response)
            return False
        match = re.search(
            r"Already Checked In at: (\d{1,2}:\d{2}[ap]m)",
            response)
        if match:
            send_message(chat_id, f"Already checked in at {match.group(1)}")
            response_json = json.loads(response)
            html_content = response_json.get("html", "")
            soup = BeautifulSoup(html_content, "html.parser")

            name_email = (
                soup.find(
                    "dt",
                    text="Name / Email:").find_next("dd").text.strip())
            name, email = name_email.split(" / ")
            location = soup.find(
                "dt", text="Location:").find_next("dd").text.strip()
            space = soup.find("dt", text="Space:").find_next("dd").text.strip()
            start_time = (
                soup.find(
                    "dt",
                    text="Start Time:").find_next("dd").text.strip())
            check_out_time = (
                soup.find(
                    "dt",
                    text="Check Out time:").find_next("dd").text.strip())

            print("Name:", name)
            print("Email:", email)
            print("Location:", location)
            print("Space:", space)
            print("Start Time:", start_time)
            print("Check Out Time:", check_out_time)

            send_message(
                chat_id,
                f"Name: {name}\nEmail: {email}\nLocation: {location}\nSpace: {space}\nStart Time: {start_time}\nCheck Out Time: {check_out_time}",
            )
            return False

        # Todo: Add successfully checkin case

        time = extract_date_time(response)
        if time is None:
            send_message(chat_id,f"Your code has been successfully executed !!!")
            return True
        time = time + timedelta(minutes=5)
        time = time - timedelta(minutes=60*8)
        time = time.astimezone(singapore_tz)  # Make `time` offset-aware
        cronjob.create_cron_job(code, time,chat_id=chat_id)
        now = datetime.now(singapore_tz)
        time_difference = time - now
        hours, remainder = divmod(time_difference.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)
        print(time.hour)
        send_message(chat_id, f"The code will be executed at {time} ({int(hours)} hours {int(minutes)} minutes later)", )

        return True

    except Exception as e:
        raise e


def sendCode(code: str) -> requests.Response:
    """Send the code to the library booking system

    Args:
        code (str): The code to send

    Returns:
        any: Any response
    """

    headers = {
        "Referer": "https://libcalendar.ntu.edu.sg/r/checkin",
    }

    payload = {
        "code": code,
    }

    url = "https://libcalendar.ntu.edu.sg/r/checkin"

    response = requests.post(url, data=payload, headers=headers)
    return response


def extract_date_time(message:str) -> date:
    # Regular expression to match the date and time format
    match = re.search(r'until (\d{1,2}:\d{2}\w{2} [A-Za-z]+, [A-Za-z]+ \d{1,2}, \d{4})', message)
    if match:
        time_str = match.group(1)
        # Convert the extracted string into a datetime object
        print(time_str)
        booking_time = datetime.strptime(time_str, "%I:%M%p %A, %B %d, %Y")
        return booking_time
    else:
        pattern = r"until (\d{1,2}:\d{2}[ap]m).*?(\d{1,2}:\d{2}[ap]m)"
        match = re.search(pattern, message)
        booking_start_time_str = match.group(1)  
        today = datetime.now(singapore_tz)
        print(booking_start_time_str)
        booking_start_time = datetime.strptime(booking_start_time_str, "%I:%M%p").replace(year=today.year, month=today.month, day=today.day)
        return booking_start_time
    return None

if __name__ == "__main__":
    # print(setWebhook(config.WEBHOOK_URL))
    app.run(host="localhost", port=1234, debug=True)
