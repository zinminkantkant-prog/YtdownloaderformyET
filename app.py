import os
import requests
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
CORS(app)  # Frontend နှင့် Connection ပြတ်တောက်မှု (CORS Error) အပြည့်အဝ ကာကွယ်ခြင်း

# YouTube Anti-Bot ကျော်လွှားသည့် Cobalt Public Engine များ
COBALT_INSTANCES = [
    "https://api.cobalt.tools/api/json",
    "https://cobalt-api.kwiatekmom.pl/api/json",
    "https://cobalt.qwik.ws/api/json"
]

def extract_via_cobalt(url, choice='mp3'):
    """Cobalt Engine ဖြင့် YouTube Anti-Bot ကို ကျော်လွှား၍ Direct MP3 Link ယူခြင်း"""
    payload = {
        "url": url,
        "downloadMode": "audio" if choice == "mp3" else "auto",
        "audioFormat": "mp3",
        "youtubeVideoCodec": "h264"
    }
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    for instance in COBALT_INSTANCES:
        try:
            res = requests.post(instance, json=payload, headers=headers, timeout=8)
            if res.status_code == 200:
                data = res.json()
                download_url = data.get("url")
                filename = data.get("filename", "audio.mp3")
                if download_url:
                    return {
                        "title": filename.replace(".mp3", ""),
                        "url": download_url
                    }
        except Exception:
            continue
    return None

def extract_via_ytdlp(url, choice='mp3'):
    """yt-dlp Fallback (iOS/Android Client Spoofing ဖြင့် Stream Link ယူခြင်း)"""
    ydl_opts = {
        'format': 'bestaudio/best' if choice == 'mp3' else 'best',
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'geo_bypass': True,
        'socket_timeout': 8,
        'extractor_args': {
            'youtube': {
                'player_client': ['ios', 'android', 'mweb']
            }
        }
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        download_url = info.get('url')
        if not download_url and 'formats' in info:
            download_url = info['formats'][-1].get('url')
        return {
            "title": info.get('title', 'YouTube Audio'),
            "url": download_url
        }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    try:
        data = request.get_json(silent=True) or request.form or {}
        url = data.get('url')
        choice = data.get('choice', 'mp3')

        if not url:
            return jsonify({'status': 'error', 'message': 'YouTube URL ထည့်သွင်းပါ'}), 400

        # ၁။ Cobalt Engine ဖြင့် Anti-Bot ကျော်လွှား၍ ဒေါင်းလုဒ် Link ရယူခြင်း
        result = extract_via_cobalt(url, choice)

        # ၂။ အကယ်၍ Cobalt မရပါက yt-dlp ဖြင့် Fallback ပြုလုပ်ခြင်း
        if not result:
            result = extract_via_ytdlp(url, choice)

        if not result or not result.get('url'):
            return jsonify({'status': 'error', 'message': 'Download Link မရရှိနိုင်ပါ'}), 400

        download_url = result['url']
        title = result['title']

        # မူရင်း index.html ၏ Key များအားလုံးနှင့် ကိုက်ညီအောင် ပြန်လည်ပေးပို့ခြင်း
        return jsonify({
            'status': 'success',
            'title': title,
            'file': download_url,        # index.html မှ file ဟု ဖတ်ပါက ရရှိရန်
            'download_url': download_url, # index.html မှ download_url ဟု ဖတ်ပါက ရရှိရန်
            'url': download_url          # index.html မှ url ဟု ဖတ်ပါက ရရှိရန်
        })

    except Exception as e:
        # Frontend ဘက်တွင် Connection Error! မပြဘဲ တိကျသော JSON အဖြေ ပို့ပေးခြင်း
        return jsonify({
            'status': 'error',
            'message': f"Error: {str(e)}"
        }), 200

# Server Internal Error ဖြစ်ပါကလည်း JSON ဖြင့် သုတ်သုတ်ပြပြ တုံ့ပြန်ပေးခြင်း
@app.errorhandler(500)
def internal_error(error):
    return jsonify({'status': 'error', 'message': 'Server တုံ့ပြန်မှု မရရှိပါ'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
