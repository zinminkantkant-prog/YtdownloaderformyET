import os
from flask import Flask, render_template, request, send_file, jsonify
import yt_dlp

app = Flask(__name__)

DOWNLOAD_DIR = 'downloads'
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/download', methods=['POST'])
def api_download():
    data = request.get_json()
    url = data.get('url')
    format_choice = data.get('format')

    if not url or not ("youtube.com" in url or "youtu.be" in url):
        return jsonify({"error": "Invalid YouTube URL"}), 400

    base_opts = {
        'source_address': '0.0.0.0',
        'retries': 10,
        'concurrent_fragment_downloads': 5,
        'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),
        'restrictfilenames': True,
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
            'format': 'bestvideo[height<=360]+bestaudio/best[height<=360]',
            'merge_output_format': 'mp4',
        }
    elif format_choice == "720p":
        ydl_opts = {
            **base_opts,
            'format': 'bestvideo[height<=720]+bestaudio/best[height<=720]',
            'merge_output_format': 'mp4',
        }
    else:
        return jsonify({"error": "Invalid format"}), 400

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

# Web ပေါ်တွင် တိုက်ရိုက်ဖွင့်ရန်နှင့် Device ထဲ Save ရန် Switch လုပ်ပေးသော Route
@app.route('/serve/<path:filename>')
def serve_file(filename):
    file_path = os.path.join(DOWNLOAD_DIR, filename)
    if os.path.exists(file_path):
        is_download = request.args.get('download', 'false').lower() == 'true'
        return send_file(file_path, as_attachment=is_download)
    return "File not found", 404

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
