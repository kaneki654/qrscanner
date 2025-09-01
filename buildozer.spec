[app]
title = QRScannerBot
package.name = qrscannerbot
package.domain = org.example
source.include_exts = py,png,jpg,json
version = 1.0
requirements = python3,kivy,opencv-python,pyzbar,discord.py,plyer
orientation = portrait
android.permissions = CAMERA, INTERNET, ACCESS_FINE_LOCATION, ACCESS_COARSE_LOCATION, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE

[buildozer]
log_level = 2
warn_on_root = 0
