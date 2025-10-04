# Requirements

## Python Version
- Python 3.11 (direkomendasikan)

## Virtual Environment
Buat dan aktifkan virtual environment:

```bash
    python -m venv .venv
    source .venv/bin/activate   # Linux/MacOS
    .venv\Scripts\activate      # Windows
```

## Install Dependencies
```bash
  pip install -r requirements.txt
```

Jika ada error saat install dlib atau face-recognition, ikuti petunjuk manual di bawah.

## Dependencies dan Cara Install Manual
```bash
  pip install opencv-python
    
  pip install numpy
    
  pip install firebase-admin
    
  pip install cvzone
    
  brew install cmake (buat MacOS)
   
```

```bash
  pip install dlib
```
 ⚠️ Jika gagal, pastikan cmake dan compiler C++ (g++, clang, atau MSVC) sudah terinstall.
 
```bash
  pip install face-recognition
```
  ⚠️ Package ini otomatis install dlib. Jika error, install dlib secara manual dulu.
  
