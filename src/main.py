import pickle
import cv2
import os
import time  # Modul untuk manajemen waktu
import cvzone
import face_recognition
import numpy as np
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
from datetime import datetime

# --- KONEKSI KE FIREBASE ---
cred = credentials.Certificate("../serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://faceattendance-84476-default-rtdb.asia-southeast1.firebasedatabase.app/',
    "storageBucket": "faceattendance-84476.firebasestorage.app"
})
bucket = storage.bucket()

# --- SETUP KAMERA DAN UI ---
cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)
imgBackground = cv2.imread('../Resources/background.png')

# --- MEMUAT GAMBAR MODE UI ---
folderModePath = '../Resources/Modes'
modePathList = os.listdir(folderModePath)
imgModeList = []
for path in modePathList:
    imgModeList.append(cv2.imread(os.path.join(folderModePath, path)))

# --- MEMUAT FILE ENCODING ---
print("Loading Encode file...")
with open('EncodeFile.p', 'rb') as file:
    encodeListKnownWithIds = pickle.load(file)
encodeListKnown, studentIds = encodeListKnownWithIds
print("Encode File Loaded")

# --- INISIALISASI VARIABEL STATE DAN TIMER ---
modeType = 0
counter = 0  # 0 = Mencari, 1 = Mengambil Data, 2 = Menampilkan Data
id = -1
imgStudent = []
studentInfo = []
display_start_time = 0
display_duration = 4  # Tampilkan info selama 4 detik

scan_y = 0 # posisi awal garis scan di area webcam (atas)
scan_direction = 1# kecepatan gerakan garis

while True:
    success, img = cap.read()
    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)
    faceCurFrame = face_recognition.face_locations(imgS)
    encodeCUrFrame = face_recognition.face_encodings(imgS, faceCurFrame)
    imgBackground[162:162 + 480, 55:55 + 640] = img

    # --- STATE 0: MENCARI WAJAH ---
    if counter == 0:
        modeType = 0
        imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

        if faceCurFrame:
            for encodeFace, faceLoc in zip(encodeCUrFrame, faceCurFrame):
                matches = face_recognition.compare_faces(encodeListKnown, encodeFace, tolerance=0.5)
                faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
                matchIndex = np.argmin(faceDis)

                # if matches[matchIndex]:
                #     id = studentIds[matchIndex]
                #     counter = 1  # Wajah ditemukan, pindah ke state pengambilan data
                #     modeType = 1  # Ganti UI ke mode aktif/profil
                #     break
                if matches[matchIndex]:
                    # print("Known Face Detected")
                    # print(studentIds[matchIndex])
                    y1, x2, y2, x1 = faceLoc
                    y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                    bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
                    if scan_y == 0:
                        scan_y = bbox[1]

                    imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)
                    id = studentIds[matchIndex]
                    if counter == 0:
                        x, y, w, h = bbox
                        y_scan = scan_y
                        if y <= y_scan <= y + h:
                            for i in range(0, w, 5):
                                alpha = i / w
                                r = int(255 * (1 - alpha))
                                g = int(255 * alpha)
                                cv2.line(imgBackground, (x + i, y_scan), (x + i + 5, y_scan), (r, g, 0), 2)

                        scan_y += scan_direction
                        if scan_y > y + h or scan_y < y:
                            scan_direction *= -1

                        cvzone.putTextRect(imgBackground, "Scanning Face...", (275, 400))
                        cv2.waitKey(1)
                        counter = 1
                        modeType = 1

    # --- STATE 1: MENGAMBIL DATA (HANYA BERJALAN SEKALI) ---
    if counter == 1:

        studentInfo = db.reference(f'Students/{id}').get()
        blob = bucket.get_blob(f'Images/{id}.jpeg')  # PASTIKAN EKSTENSI FILE BENAR (.png, .jpg, dll)
        if blob:
            array = np.frombuffer(blob.download_as_string(), np.uint8)
            imgStudent = cv2.imdecode(array, cv2.COLOR_BGRA2BGR)

        datetimeObject = datetime.strptime(studentInfo['last_attendance_time'], "%Y-%m-%d %H:%M:%S")
        secondsElapsed = (datetime.now() - datetimeObject).total_seconds()

        if secondsElapsed > 30:
            ref = db.reference(f'Students/{id}')
            studentInfo['total_attendance'] += 1
            ref.child('total_attendance').set(studentInfo['total_attendance'])
            ref.child('last_attendance_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            # modeType sudah 1, biarkan untuk menampilkan data
        else:
            modeType = 3  # "Already Marked"

        display_start_time = time.time()  # Mulai timer
        counter = 2  # Pindah ke state menampilkan data

    # --- STATE 2: MENAMPILKAN DATA SELAMA DURASI TERTENTU ---
    if counter == 2:
        # Cek apakah durasi tampilan sudah berakhir
        if time.time() - display_start_time > display_duration:
            counter = 0  # Reset ke state awal
            studentInfo = []  # Kosongkan data
            imgStudent = []
        else:
            # Jika absensi berhasil, tampilkan data di atas template mode 1
            if modeType != 3:
                # Ganti background ke template mode 1 (profil)
                imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[1]

                # Tampilkan semua data mahasiswa
                (w, h), _ = cv2.getTextSize(studentInfo['name'], cv2.FONT_HERSHEY_COMPLEX, 1, 1)
                offset = (414 - w) // 2
                cv2.putText(imgBackground, str(studentInfo['name']), (808 + offset, 445), cv2.FONT_HERSHEY_COMPLEX, 1,
                            (50, 50, 50), 1)
                cv2.putText(imgBackground, str(studentInfo['total_attendance']), (861, 125), cv2.FONT_HERSHEY_COMPLEX,
                            1, (255, 255, 255), 2)
                cv2.putText(imgBackground, str(studentInfo['major']), (1006, 550), cv2.FONT_HERSHEY_COMPLEX, 0.5,
                            (255, 255, 255), 1)
                cv2.putText(imgBackground, str(id), (1006, 493), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                cv2.putText(imgBackground, str(studentInfo['standing']), (910, 625), cv2.FONT_HERSHEY_COMPLEX, 0.6,
                            (100, 100, 100), 1)
                cv2.putText(imgBackground, str(studentInfo['year']), (1025, 625), cv2.FONT_HERSHEY_COMPLEX, 0.6,
                            (100, 100, 100), 1)
                cv2.putText(imgBackground, str(studentInfo['starting_year']), (1125, 625), cv2.FONT_HERSHEY_COMPLEX,
                            0.6, (100, 100, 100), 1)

                if len(imgStudent) > 0:
                    imgStudentResized = cv2.resize(imgStudent, (216, 216))
                    imgBackground[175:175 + 216, 909:909 + 216] = imgStudentResized

            # Jika sudah absen, hanya tampilkan mode 3
            else:
                imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

    cv2.imshow('Background', imgBackground)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()