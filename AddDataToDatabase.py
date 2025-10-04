import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://faceattendance-84476-default-rtdb.asia-southeast1.firebasedatabase.app/'
})

ref = db.reference('Students')

data = {
    "5026231082":
        {
            "name": "Naufal Zaky Nugraha",
            "major": "Information System",
            "starting_year": 2023,
            "total_attendance": 7,
            "standing": "6",
            "year": 4,
            "last_attendance_time": "2025-10-03 00:54:34",
        },
    "5026231151":
        {
            "name": "Kayla Nathania Azzahra",
            "major": "Information System",
            "starting_year": 2023,
            "total_attendance": 7,
            "standing": "6",
            "year": 4,
            "last_attendance_time": "2025-10-03 00:54:34",
        },
"5026231170":
        {
            "name": "Tahiyyah Mufhimah",
            "major": "Information System",
            "starting_year": 2023,
            "total_attendance": 7,
            "standing": "6",
            "year": 4,
            "last_attendance_time": "2025-10-03 00:54:34",
        }
}

for key, value in data.items():
    ref.child(key).set(value)