import requests
from flask import Flask, request
import schedule
import time
import threading
import re
from datetime import datetime
from dataclasses import dataclass

app = Flask(__name__)

# Replace 'YOUR_BOT_TOKEN' with the actual token provided by BotFather
BOT_TOKEN = '7663753275:AAFeMC5sGWk00mWgQHPTx-waGh64i3MLGR8'

@app.route('/webhook', methods=['POST'])
def webhook():
    # Get the JSON data from the incoming request
    data = request.json

    # Handle the message
    if 'message' in data:
        chat_id = data['message']['chat']['id']
        text = data['message'].get('text', '')
        # Check if the message is a command
        if text.startswith('/'):
            print(f"chat_id: {chat_id}")
            print(f"text: {text}")
            handle_command(chat_id, text)
        else:
            # Handle normal text message (for example, echo it back)
            xulicode(chat_id, text)

    return "OK", 200

def handle_command(chat_id, command):
    # Basic command handling
    if command == '/start':
        send_message(chat_id, "Welcome! I'm your bot. How can I assist you?")
    elif command == '/help':
        send_message(chat_id, "Available commands:\n/start - Start the bot\n/help - Show this help message")
    elif command == '/pending':
        cnt = 0
        for code in pending:
            cnt = cnt+1
            send_message(chat_id,f"code number {cnt}:")
            send_message(chat_id,f"Code: {code.code}")
            send_message(chat_id,f"Remain time:{code.time/3600} hour(s)")
    else:
        send_message(chat_id, "Sorry, I didn't understand that command.")
url1 = 'https://libcalendar.ntu.edu.sg/r/checkin'

def checkin(text: str):
    payload = {
        "code": text,
    }
    headers = {
        'Referer': 'https://libcalendar.ntu.edu.sg/r/checkin',
    }
    response = requests.post(url1, data=payload, headers=headers)
    print(response.text)

def extract_booking_time(message):
    # Regular expression to match the date and time format
    match = re.search(r'until (\d{1,2}:\d{2}\w{2} [A-Za-z]+, [A-Za-z]+ \d{1,2}, \d{4})', message)
    if match:
        time_str = match.group(1)
        # Convert the extracted string into a datetime object
        print(time_str)
        booking_time = datetime.strptime(time_str, "%I:%M%p %A, %B %d, %Y")
        return booking_time
    return None
class checkincode:
    def __init__(self, code, time):
        self.code = code
        self.time = time

pending=[]
def xulicode(chat_id, text):
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
    payload1 = {
        "code": text,
    }
    proxies = {
        'http': 'http://proxy.pythonanywhere.com:3128',
        'https': 'http://proxy.pythonanywhere.com:3128',
    }
    headers = {
        'Referer': 'https://libcalendar.ntu.edu.sg/r/checkin',
    }
    response = requests.post(url1, data=payload1, headers=headers)
    if(response.text=="Unable to find booking matching code"):
        payload = {'chat_id': chat_id, 'text': "Wrong code"}
        requests.post(url, json=payload)
    else:
        payload = {'chat_id': chat_id, 'text': "Received code"}
        requests.post(url, json=payload)
        timestamp = extract_booking_time(response.text).timestamp()
        current_timestamp = time.time()
        payload = {'chat_id': chat_id, 'text': f"Your booking will be done in {current_timestamp-timestamp} second"}
        requests.post(url, json=payload)
        p1=checkincode(text,timestamp)
        pending.append(p1)
        

def send_message(chat_id, text):
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
    payload = {'chat_id': chat_id, 'text': text}
    requests.post(url, json=payload)
        

def prcocess_code():
    while True:
        for code in pending:
            print(code.code)
            current_timestamp = time.time()
            if(current_timestamp>code.time):
                checkin(code.code)
        time.sleep(30)

thread = threading.Thread(target=prcocess_code)
thread.start()

if __name__ == '__main__':
    # Start the Flask server on port 5000
    app.run(host='0.0.0.0', port=5000)
