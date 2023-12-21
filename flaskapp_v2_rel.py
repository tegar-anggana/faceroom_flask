from flask import Flask, request, jsonify
from sklearn.neighbors import KNeighborsClassifier
import cv2
import pickle
import os
import csv
from datetime import datetime

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

        for (x, y, w, h) in faces:
            # Crop the detected face
            crop_img = img[y:y + h, x:x + w, :]
            resized_img = cv2.resize(crop_img, (50, 50)).flatten().reshape(1, -1)

            # Perform face recognition
            output = knn.predict(resized_img)

            # Get current timestamp
            ts = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")

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

        # Create 'Attendance' directory if it doesn't exist
        attendance_dir = 'Attendance'
        os.makedirs(attendance_dir, exist_ok=True)

        # Store the detected faces information in a CSV file with the current date and timestamp
        csv_filename = f"{attendance_dir}/Attendance_{ts}.csv"
        with open(csv_filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['NAME', 'TIME'])  # Header row
            writer.writerows(all_faces)

        # Create 'Results' directory if it doesn't exist
        results_dir = 'Results'
        os.makedirs(results_dir, exist_ok=True)

        # Save the resulting image in the 'Results' directory with the current date and timestamp
        result_img_filename = f"{results_dir}/Result_{ts}.jpg"
        cv2.imwrite(result_img_filename, img)

        # Return a success response
        response = {'status': 'success', 'message': 'Image processed successfully.'}
        return jsonify(response)

    except Exception as e:
        # Return an error response
        response = {'status': 'error', 'message': str(e)}
        return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
