import requests
from flask import Flask, request

import re
from datetime import datetime, date
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
                data["message"]["message_id"], user, chat, data["message"]["date"], text
            )

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


def handle_command(user_id: str, chat_id: str, command: str):
    """_summary_

    Args:
        chat_id (str): _description_
        text (str): _description_
    """

    match command:
        case "/start":
            send_message(chat_id, "Welcome! I'm your bot. How can I assist you?")
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
    """Send message to telegram"""
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
        url = f"https://api.telegram.org/bot{config.BOT_TOKEN}/setWebhook?url={url}"
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
        response = sendCode(code)
        print(response)
        if response == "Unable to find booking matching code":
            send_message(chat_id, response)
            return False
        match = re.search(r"Already Checked In at: (\d{1,2}:\d{2}[ap]m)", response)
        if match:
            send_message(chat_id, f"Already checked in at {match.group(1)}")
            return False
        else:
            time = extract_date_time(response)
            print(time)
            if time is None:
                return False
            cronjob.create_cron_job(code, time)
            return True

    except Exception as e:
        raise e


def sendCode(code: str) -> any:
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
    return response.text


def extract_date_time(res: str) -> date:
    """Extract the date and time from the response

    Args:
        res (str): The response from the server

    Raises:
        e: Error when parsing the time

    Returns:
        datetime: The datetime object of the booking time
    """
    pattern = r"until (\d{1,2}:\d{2}[ap]m) ([A-Za-z]+), ([A-Za-z]+ \d{1,2}, \d{4})"
    match = re.search(pattern, res)
    
    # If the response is in the format "until 9:10am Tuesday, October 29, 2024", extract the date and time
    # An example is
    #   'Unable to Check In for this booking until 10:55am Friday, November 8, 2024 (booking starts at 11:00am Friday, November 8, 2024).'
    try:
        if match:
            time_str = match.group(1) # "9:10am"
            weekday_str = match.group(2) # "Tuesday"
            date_str = match.group(3) # "October 29, 2024"
            
            # Convert the date and time to a datetime object
            
            return datetime.strptime(f"{date_str} {time_str}", "%B %d, %Y %I:%M%p")
        
        pattern = r"until (\d{1,2}:\d{2}[ap]m).*?(\d{1,2}:\d{2}[ap]m)"
        
        # If the response is in the format "Unable to Check In for this booking until 7:55pm (booking starts at 8:00pm).", extract the time
        # An example is
        #   'Unable to Check In for this booking until 8:55am Saturday, November 2, 2024 (booking starts at 9:00am Saturday, November 2, 2024).'
        #   This is likely the case when the booking is available on the same day
        match = re.search(pattern, res) # "7:55am"
        if match:
            check_in_time = match.group(1)
            return datetime.strptime(check_in_time, "%I:%M%p")
        else:
            # Likely due to already checkedin
            return None
        
    except Exception as e:
        # Time is not in the correct format
        raise e



if __name__ == "__main__":
    # print(setWebhook(config.WEBHOOK_URL))
    app.run(host="localhost", port=1234, debug=True)
