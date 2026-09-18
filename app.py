import os
from flask import Flask, render_template, request, send_file, jsonify
import yt_dlp

app = Flask(__name__)

# File Path များကို ပိုမိုတိကျစေရန် Absolute Path သုံးထားပါသည်
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOWNLOAD_DIR = os.path.join(BASE_DIR, 'downloads')

if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/download', methods=['POST'])
def api_download():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid request parameters"}), 400

    url = data.get('url')
    format_choice = data.get('format')

    if not url or not ("youtube.com" in url or "youtu.be" in url):
        return jsonify({"error": "Invalid YouTube URL"}), 400

    # 'source_address': '0.0.0.0' ကို ဖယ်ရှားထားပါသည် (Connection error ကို ဖြေရှင်းပေးပါသည်)
    base_opts = {
        'retries': 10,
        'concurrent_fragment_downloads': 5,
        'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),
        'restrictfilenames': True,
        'nocheckcertificate': True,
        'quiet': True,
        'no_warnings': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }

    if format_choice == "mp3":
        ydl_opts = {
            **base_opts,
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '128',
            }],
        }
    elif format_choice == "360p":
        ydl_opts = {
            **base_opts,
            'format': 'best[height<=360]/bestvideo[height<=360]+bestaudio/best',
            'merge_output_format': 'mp4',
        }
    elif format_choice == "720p":
        ydl_opts = {
            **base_opts,
            'format': 'best[height<=720]/bestvideo[height<=720]+bestaudio/best',
            'merge_output_format': 'mp4',
        }
    else:
        return jsonify({"error": "Invalid format choice"}), 400

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(url, download=True)

        return jsonify({"status": "success", "message": "Download Completed!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/files', methods=['GET'])
def list_files():
    try:
        files = os.listdir(DOWNLOAD_DIR)
        mp3_files = [f for f in files if f.endswith('.mp3')]
        mp4_files = [f for f in files if f.endswith('.mp4')]
        return jsonify({"mp3": mp3_files, "mp4": mp4_files})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/serve/<path:filename>')
def serve_file(filename):
    file_path = os.path.join(DOWNLOAD_DIR, filename)
    if os.path.exists(file_path):
        is_download = request.args.get('download', 'false').lower() == 'true'
        return send_file(file_path, as_attachment=is_download)
    return "File not found", 404

if __name__ == '__main__':
    # Localhost 127.0.0.1 ဖြင့် ပြောင်းလဲထားပါသည်
    app.run(debug=False, host="127.0.0.1", port=5000)
