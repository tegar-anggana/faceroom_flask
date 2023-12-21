import csv

def csv_to_string(filename):
    with open(filename, 'r') as file:
        # Create a CSV reader object
        csv_reader = csv.reader(file)

        # Skip the header row
        next(csv_reader)

        # Extract all the remaining rows and join them into a single string
        output_string = '\n'.join([','.join(row) for row in csv_reader])

    return output_string

# filename = './Attendance/Attendance_01-12-2023_16-27-09.csv'
# print(csv_to_string(filename))

from flask import Flask, request
import requests

app = Flask(__name__)

BOT_TOKEN = '6593538231:AAG_lR9GMWRmnFIRbRsB6gW0c-D4a8U3bm0'
TELEGRAM_API_URL = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
CHAT_ID = '-4000261630'

def send_message_to_telegram(text):
   data = {
       'chat_id': CHAT_ID,
       'text': text,
       'parse_mode': 'HTML'
   }
   response = requests.post(TELEGRAM_API_URL, json=data)
   return response.json()

@app.route('/send_message')
def send_message():
    filename = './Attendance/Attendance_01-12-2023_16-27-09.csv'
    print(csv_to_string(filename))
    data = csv_to_string(filename)
    report = f'Daftar hadir hari ini:\n{data}'
    send_message_to_telegram(report)
    return "Message sent successfully", 200

if __name__ == '__main__':
   app.run(debug=True)