import cv2
import os

def capture_and_save_image():
    # Menghapus file representations_vgg_face.pkl jika exist
    representations_file = "known_faces/representations_vgg_face.pkl"
    if os.path.exists(representations_file):
        os.remove(representations_file)
        print(f"File {representations_file} telah dihapus.")

    # Meminta nama orang
    nama_orang = input("Masukkan nama orang: ")

    # Inisialisasi kamera
    camera = cv2.VideoCapture(0)

    # Membuka jendela kamera
    while True:
        ret, frame = camera.read()
        cv2.imshow("Press 'c' to capture", frame)

        # Menunggu tombol 'c' ditekan
        key = cv2.waitKey(1)
        if key == ord('c'):
            break

    # Menyimpan gambar dengan nama yang sesuai di direktori known_faces
    directory = "known_faces"
    if not os.path.exists(directory):
        os.makedirs(directory)

    file_path = os.path.join(directory, f"{nama_orang}.jpg")
    cv2.imwrite(file_path, frame)
    print(f"Gambar telah disimpan di: {file_path}")

    # Menutup jendela kamera
    camera.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    capture_and_save_image()
