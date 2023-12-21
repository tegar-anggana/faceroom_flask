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

@app.route('/send_message', methods=['POST'])
def send_message():
   data = request.get_json()
   text = data.get('text')
   if text:
       send_message_to_telegram(text)
       return "Message sent successfully", 200
   else:
       return "Message is required", 400

if __name__ == '__main__':
   app.run(debug=True)