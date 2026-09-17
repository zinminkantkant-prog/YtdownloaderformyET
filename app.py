import os
import tempfile
from flask import Flask, render_template, request, jsonify
import yt_dlp

app = Flask(__name__)

def get_cookie_path():
    """Render Secret File သို့မဟုတ် Environment Variable သို့မဟုတ် Local ဖိုင်မှ
    Cookie လမ်းကြောင်းကို အစီအစဉ်အတိုင်း စစ်ဆေးပေးသည့် စနစ်"""
    
    # ၁။ Render Secret File (/etc/secrets/cookies.txt) ရှိမရှိ စစ်ခြင်း
    render_secret_path = '/etc/secrets/cookies.txt'
    if os.path.exists(render_secret_path):
        return render_secret_path
        
    # ၂။ Render Environment Variable (YOUTUBE_COOKIES) မှ ဖတ်ခြင်း
    cookie_content = os.environ.get('YOUTUBE_COOKIES')
    if cookie_content:
        temp_cookie_path = os.path.join(tempfile.gettempdir(), 'cookies.txt')
        with open(temp_cookie_path, 'w', encoding='utf-8') as f:
            f.write(cookie_content)
        return temp_cookie_path
        
    # ၃။ Local Root Directory ထဲရှိ cookies.txt ဖိုင်ကို စစ်ခြင်း
    if os.path.exists('cookies.txt'):
        return 'cookies.txt'
        
    return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    data = request.json or request.form
    url = data.get('url')
    choice = data.get('choice', 'mp3')

    if not url:
        return jsonify({'status': 'error', 'message': 'YouTube URL ထည့်သွင်းပါ'}), 400

    ydl_opts = {
        'format': 'bestaudio/best' if choice == 'mp3' else 'bestvideo+bestaudio/best',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
        # YouTube Bot Check ရှောင်လွှဲရန် Client Settings
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'ios', 'mweb']
            }
        }
    }

    # Cookie ဖိုင် လမ်းကြောင်း ညွှန်းပေးခြင်း
    cookie_path = get_cookie_path()
    if cookie_path:
        ydl_opts['cookiefile'] = cookie_path

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            return jsonify({
                'status': 'success',
                'title': info.get('title'),
                'file': filename
            })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
