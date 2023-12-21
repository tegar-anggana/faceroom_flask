from flask import Flask, request, jsonify
from datetime import datetime
import cv2
import os
import csv
import requests
from deepface import DeepFace

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

@app.route('/')
def hello():
    return jsonify(message='hello')

@app.route('/upload', methods=['POST'])
def upload_image():
    timestamp = datetime.now()
    ts = timestamp.strftime("%d-%m-%Y_%H-%M-%S")
    
    source_faces = request.files['image'] # IMAGE FROM CLIENT HTTP
    sources_dir = 'Sources'
    os.makedirs(sources_dir, exist_ok=True)
    image_path = os.path.join(sources_dir, f"Source_{source_faces.filename}")
    source_faces.save(image_path) # SAVE IMAGE FROM CLIENT HTTP
    
    single_faces_dir = f'single_faces/{ts}/'
    known_faces_dir = 'known_faces'
    results_dir = 'Results' # DETECTION + RECOGNITION RESULT DIR
    all_faces = set() # RECOGNIZED FACES FOR CSV REPORT
    os.makedirs(single_faces_dir, exist_ok=True)
    os.makedirs(known_faces_dir, exist_ok=True)
    os.makedirs(results_dir, exist_ok=True)
    result_img_filename = f"{results_dir}/Result_{ts}.jpg"

    img = cv2.imread(image_path)
    
    # FACE RECOGNITION & LABELING
    face_objs = DeepFace.extract_faces(img_path=image_path, 
                                target_size=(224, 224), 
                                detector_backend="fastmtcnn",
                                enforce_detection=False,
    )
    
    margin = 20
    
    for i, obj in enumerate(face_objs):
        box = obj['facial_area']
        
        # Expand the bounding box coordinates by the specified margin
        expanded_box = [max(0, int(box['x']) - margin),
                        max(0, int(box['y']) - margin),
                        min(img.shape[1], int(box['x'] + box['w']) + margin),
                        min(img.shape[0], int(box['y'] + box['h']) + margin)]

        # Extract the region of interest (ROI) for each face using the expanded bounding box
        face_roi = img[expanded_box[1]:expanded_box[3], expanded_box[0]:expanded_box[2]]
        
        # Save each face
        face_filename = f'face_{i + 1}.jpg'
        cur_face_dir = f'{single_faces_dir}{face_filename}'
        cv2.imwrite(cur_face_dir, face_roi)
        
        # Face recognition
        dfs = DeepFace.find(img_path=cur_face_dir, db_path=known_faces_dir, enforce_detection=False)

        detection_data = {
            "id": i,
            "label": None,
            "skor": None,
            "facial_area": expanded_box
        }

        # dfs = lists of ranked familiar faces, so dfs[0] would be the most similar (lowest VGG-Face_cosine score)
        if dfs[0].shape[0] == 0:
            detection_data['label'] = 'TIDAK DIKENAL' 
            detection_data['skor'] = '-'
            box_and_label_color = (0, 0, 255) # red color
        else:
            best_match = dfs[0].iloc[0]['VGG-Face_cosine']
            filename_with_ext = os.path.basename(dfs[0].iloc[0]['identity'])
            filename, file_ext = os.path.splitext(filename_with_ext)
            detection_data['label'] = filename
            detection_data['skor'] = best_match
            all_faces.add((detection_data['label'], ts))
            box_and_label_color = (0, 255, 0) # green color
        
        # Draw bounding box and label on the original image using the expanded coordinates
        cv2.rectangle(img, (expanded_box[0], expanded_box[1]), (expanded_box[2], expanded_box[3]), box_and_label_color, 2)
        cv2.putText(img, detection_data['label'], (expanded_box[0], expanded_box[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, box_and_label_color, 2)
    
    cv2.imwrite(result_img_filename, img) # SAVE RESULT IMAGE

    attendance_dir = 'Attendance'
    os.makedirs(attendance_dir, exist_ok=True) # CSV ATTENDANCE DIR
    csv_filename = f"{attendance_dir}/Attendance_{ts}.csv"
    all_faces_list = [list(t) for t in all_faces]
    with open(csv_filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['NAME', 'TIME'])  # Header row
        writer.writerows(all_faces_list)
    
    data = csv_to_string(csv_filename)
    report = f'Daftar hadir hari ini:\n{data}'
    
    send_photo_to_telegram(result_img_filename, report) # KIRIM GAMBAR DAN CAPTION KE TELEGRAM 
    
    response = {'status': 'success', 'message': 'Image processed successfully.'}
    return jsonify(response)

    
    # Return an error response
    response = {'status': 'error', 'message': str(e)}
    return jsonify(response)



if __name__ == '__main__':
    app.run(debug=True)

