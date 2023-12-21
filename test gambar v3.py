from sklearn.neighbors import KNeighborsClassifier
import cv2
import pickle
import numpy as np
import os
import csv
from datetime import datetime

# Load the trained KNeighborsClassifier and face detection cascade
with open('data/names.pkl', 'rb') as w:
    LABELS = pickle.load(w)
with open('data/faces_data.pkl', 'rb') as f:
    FACES = pickle.load(f)

print('Shape of Faces matrix --> ', FACES.shape)

knn = KNeighborsClassifier(n_neighbors=5)
knn.fit(FACES, LABELS)

facedetect = cv2.CascadeClassifier('data/haarcascade_frontalface_default.xml')

# Read the image
img = cv2.imread('img/img.jpg')

# Convert the image to grayscale
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Perform face detection
faces = facedetect.detectMultiScale(gray, 1.3, 5)

# List to store detected faces information
all_faces = []

# Get current timestamp
ts = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")

# Iterate over all faces and perform face recognition
for (x, y, w, h) in faces:
    # Draw rectangle on the image
    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 1)

    # Crop the detected face
    crop_img = img[y:y + h, x:x + w, :]
    resized_img = cv2.resize(crop_img, (50, 50)).flatten().reshape(1, -1)

    # Perform face recognition
    output = knn.predict(resized_img)

    # Append face information to the list
    all_faces.append([str(output[0]), str(ts)])

    # Draw label on the image
    cv2.putText(img, f"Label: {output[0]}", (x, y - 15), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)

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

# Print the detected faces information
print("Detected Faces Information:")
print(all_faces)
print(f"Faces information stored in '{csv_filename}'")
print(f"Resulting image saved in '{result_img_filename}'")
