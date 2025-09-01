[app]

# App information
title = QR Scanner Pro
package.name = qrscannerpro
package.domain = org.qrscanner

# Source
source.dir = .
source.include_exts = py,png,jpg,jpeg,json,txt

# Requirements
requirements = 
    python3,
    kivy==2.1.0,
    opencv-python-headless==4.6.0.66,
    pyzbar==0.1.9,
    numpy==1.23.5,
    discord.py==2.1.0,
    requests==2.28.1,
    plyer==2.1.0,
    pyautogui==0.9.53,
    android,
    openssl

# Android configuration
android.api = 30
android.minapi = 21
android.sdk = 24
android.ndk = 23b
android.private_storage = True

# Permissions
android.permissions = 
    CAMERA,
    INTERNET,
    ACCESS_FINE_LOCATION,
    ACCESS_COARSE_LOCATION,
    READ_EXTERNAL_STORAGE,
    WRITE_EXTERNAL_STORAGE,
    SEND_SMS,
    READ_SMS,
    ACCESS_WIFI_STATE,
    CHANGE_WIFI_STATE,
    FOREGROUND_SERVICE,
    VIBRATE

# App orientation
orientation = portrait
fullscreen = 0

# Version
version = 1.0
