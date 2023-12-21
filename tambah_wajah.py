import cv2
import os

def capture_and_save_image():
    # Meminta nama orang
    nama_orang = input("Masukkan nama orang: ")

    # Inisialisasi kamera
    camera = cv2.VideoCapture(0)

    # Menangkap frame
    ret, frame = camera.read()

    # Menyimpan gambar dengan nama yang sesuai di direktori known_faces
    if ret:
        directory = "known_faces"
        if not os.path.exists(directory):
            os.makedirs(directory)

        file_path = os.path.join(directory, f"{nama_orang}.jpg")
        cv2.imwrite(file_path, frame)
        print(f"Gambar telah disimpan di: {file_path}")
    else:
        print("Gagal menangkap gambar.")

    # Melepas kamera
    camera.release()

if __name__ == "__main__":
    capture_and_save_image()
