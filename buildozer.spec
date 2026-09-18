[app]
title = YT Downloader
package.name = ytdownloader
package.domain = org.zmk
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,html,css,js
version = 0.1
requirements = python3,kivy==2.3.0,flask,yt-dlp,requests,urllib3,certifi,android,pyjnius
orientation = portrait
fullscreen = 0
android.permissions = INTERNET, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a
p4a.branch = master

[buildozer]
log_level = 2
warn_on_root = 1
