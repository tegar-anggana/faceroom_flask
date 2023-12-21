from flask import Flask, request, jsonify
from sklearn.neighbors import KNeighborsClassifier
from datetime import datetime
import cv2
import pickle
import os
import csv
import requests

# TELEGRAM BOT
BOT_TOKEN = '6593538231:AAG_lR9GMWRmnFIRbRsB6gW0c-D4a8U3bm0'
CHAT_ID = '-4000261630'

# Untuk pesan telegram bot 
def csv_to_string(filename):
    with open(filename, 'r') as file:
        # Create a CSV reader object
        csv_reader = csv.reader(file)

        # Skip the header row
        next(csv_reader)

        # Extract all the remaining rows and join them into a single string
        output_string = '\n'.join([','.join(row) for row in csv_reader])

    return output_string

# Untuk kirim pesan telegram dari bot telegram
def send_message_to_telegram(text):
   telegram_send_message_api_url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
   data = {
       'chat_id': CHAT_ID,
       'text': text,
       'parse_mode': 'HTML'
   }
   response = requests.post(telegram_send_message_api_url, json=data)
   return response.json()

# Untuk kirim gambar ke telegram melalui bot telegram
def send_photo_to_telegram(photo_path, caption=""):
    print(photo_path)
    telegram_send_photo_api_url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto'
    files = {
        "photo": (photo_path, open(photo_path, "rb")),
    }
    data = {
        "chat_id": CHAT_ID,
        "caption": caption,
    }
    response = requests.post(telegram_send_photo_api_url, files=files, data=data)
    return response.json()

app = Flask(__name__)

# Load the trained KNeighborsClassifier and face detection cascade
with open('data/names.pkl', 'rb') as w:
    LABELS = pickle.load(w)
with open('data/faces_data.pkl', 'rb') as f:
    FACES = pickle.load(f)

print('Shape of Faces matrix --> ', FACES.shape)

knn = KNeighborsClassifier(n_neighbors=5)
knn.fit(FACES, LABELS)

facedetect = cv2.CascadeClassifier('data/haarcascade_frontalface_default.xml')

@app.route('/')
def hello():
    return jsonify(message='hello')

@app.route('/upload', methods=['POST'])
def upload_image():
    try:
        # Get the image from the request
        image_file = request.files['image']
        
        # Create 'Sources' directory if it doesn't exist
        sources_dir = 'Sources'
        os.makedirs(sources_dir, exist_ok=True)

        # Save the image to 'Sources/<file-name>'
        # image_path = os.path.join(sources_dir, image_file.filename)
        image_path = os.path.join(sources_dir, f"Source_{image_file.filename}")
        image_file.save(image_path)

        # Read the uploaded image
        img = cv2.imread(image_path)

        # Convert the image to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Perform face detection
        faces = facedetect.detectMultiScale(gray, 1.3, 5)

        # List to store detected faces information
        all_faces = []
        
        # Get current timestamp
        ts = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")

        for (x, y, w, h) in faces:
            # Crop the detected face
            crop_img = img[y:y + h, x:x + w, :]
            resized_img = cv2.resize(crop_img, (50, 50)).flatten().reshape(1, -1)

            # Perform face recognition
            output = knn.predict(resized_img)

            # Append face information to the list
            all_faces.append([str(output[0]), str(ts)])

            # Draw rectangle on the image
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 1)

            # Define font settings
            font = cv2.FONT_HERSHEY_COMPLEX
            font_scale = 0.5
            font_thickness = 1
            font_color = (255, 255, 255)

            # Draw text with black outline
            cv2.putText(img, f"{output[0]}", (x, y - 15), font, font_scale, (0, 0, 0), font_thickness + 1, cv2.LINE_AA)
            cv2.putText(img, f"{output[0]}", (x, y - 15), font, font_scale, font_color, font_thickness, cv2.LINE_AA)

        # Create 'Results' directory if it doesn't exist
        results_dir = 'Results'
        os.makedirs(results_dir, exist_ok=True)

        # Save the resulting image in the 'Results' directory with the current date and timestamp
        result_img_filename = f"{results_dir}/Result_{ts}.jpg"
        cv2.imwrite(result_img_filename, img)        
        
        # Create 'Attendance' directory if it doesn't exist
        attendance_dir = 'Attendance'
        os.makedirs(attendance_dir, exist_ok=True)

        # Store the detected faces information in a CSV file with the current date and timestamp
        csv_filename = f"{attendance_dir}/Attendance_{ts}.csv"
        with open(csv_filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['NAME', 'TIME'])  # Header row
            writer.writerows(all_faces)
        
        # Kirim pesan telegram ke grup melalui bot untuk report
        data = csv_to_string(csv_filename)
        report = f'Daftar hadir hari ini:\n{data}'
        # send_message_to_telegram(report)
        
        # Kirim juga gambar hasil labeling untuk report
        send_photo_to_telegram(result_img_filename, report)
        # Return a success response
        response = {'status': 'success', 'message': 'Image processed successfully.'}
        return jsonify(response)

    except Exception as e:
        # Return an error response
        response = {'status': 'error', 'message': str(e)}
        return jsonify(response)



if __name__ == '__main__':
    app.run(debug=True)

