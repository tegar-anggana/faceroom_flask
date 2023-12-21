from flask import Flask, request
import requests

app = Flask(__name__)

BOT_TOKEN = '6593538231:AAG_lR9GMWRmnFIRbRsB6gW0c-D4a8U3bm0'
TELEGRAM_API_URL = f'https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto'
CHAT_ID = '-4000261630'

def send_photo(photo_path, caption=""):
    files = {
        "photo": (photo_path, open(photo_path, "rb")),
    }

    data = {
        "chat_id": CHAT_ID,
        "caption": caption,
    }

    response = requests.post(TELEGRAM_API_URL, files=files, data=data)

    return response.json()

@app.route('/send_message')
def send_message():
    photo_path = './Results/Result_03-12-2023_20-26-02.jpg'
    caption = 'gas'
    result = send_photo(photo_path, caption)
    print(result)   
    return "Message sent successfully", 200

if __name__ == '__main__':
   app.run(debug=True)