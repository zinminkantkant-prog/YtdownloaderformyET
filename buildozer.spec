[app]
title = YT Downloader
package.name = ytdownloader
package.domain = org.zmk
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,html,css,js
version = 0.1
requirements = python3,kivy,flask,yt-dlp,pyjnius,android,urllib3,certifi
orientation = portrait
fullscreen = 0
android.permissions = INTERNET, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21

[buildozer]
log_level = 2
warn_on_root = 1
