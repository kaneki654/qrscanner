[app]

# App information
title = QR Scanner Pro
package.name = qrscannerpro
package.domain = org.qrscanner

# Source
source.dir = .
source.include_exts = py,png,jpg,jpeg,json,txt,spec

# Requirements (optimized for Android)
requirements = 
    python3,
    kivy==2.2.1,
    opencv-python-headless==4.8.1.78,
    pyzbar==0.1.9,
    numpy==1.24.4,
    requests==2.31.0,
    plyer==2.1.0,
    android,
    openssl

# Exclude problematic packages for Android
source.exclude_patterns = 
    .git,
    .github,
    __pycache__,
    *.pyc,
    *.pyo,
    venv,
    .vscode,
    .idea,
    *.spec,
    *.log,
    bin,
    .buildozer

# Android configuration
android.api = 33
android.minapi = 21
android.sdk = 26
android.ndk = 23b
android.ndk_path = 
android.sdk_path = 
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
version.regex = __version__ = '(.*)'
version.filename = %(source.dir)s/main.py

# Build options
log_level = 2
warn_on_root = 1

# Presplash and icon (optional)
# presplash.filename = %(source.dir)s/data/presplash.png
# icon.filename = %(source.dir)s/data/icon.png

# P4a options
p4a.branch = master
android.arch = armeabi-v7a

# Add JNI dependencies if needed
# android.add_jars = 
# android.add_aars = 
