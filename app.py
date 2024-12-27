from flask import Flask, render_template, request, send_file, jsonify, make_response, Response
import yt_dlp
import os
import re
import io
import logging
import glob

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Define download folder
DOWNLOAD_FOLDER = "downloads"
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_info', methods=['POST'])
def video_info():
    url = request.form.get('url')
    
    if not url:
        return jsonify({"error": "Please provide a valid URL."}), 400

    ydl_opts = {'quiet': True}
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return jsonify({
                "title": info['title'],
                "duration": format_duration(info['duration']),
                "views": format_views(info['view_count'])
            })
    except Exception as e:
        logging.error(f"Error fetching video info: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/convert', methods=['POST'])
def convert():
    url = request.form.get('url')
    format_type = request.form.get('format')
    quality = request.form.get('quality')

    if not url or not format_type:
        return jsonify({"error": "Please provide a valid URL and format."}), 400

    ydl_opts = {
        'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
        'format': 'bestaudio/best' if format_type == 'mp3' else 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4'
    }

    if format_type == 'mp3':
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': quality,
        }]

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info['title']
            safe_title = re.sub(r'[^\w\-_\. ]', '_', title)
            expected_filename = f"{safe_title}.{format_type}"
            
            # Find the actual file
            files = glob.glob(os.path.join(DOWNLOAD_FOLDER, f"*{format_type}"))
            if not files:
                raise FileNotFoundError(f"No {format_type} file found in {DOWNLOAD_FOLDER}")
            
            filepath = files[0]  # Use the first matching file
            actual_filename = os.path.basename(filepath)

        return send_file(filepath, as_attachment=True, download_name=actual_filename)
    except Exception as e:
        logging.error(f"Error during conversion: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        # Clean up the downloaded file
        if 'filepath' in locals() and os.path.exists(filepath):
            os.remove(filepath)

def format_duration(seconds):
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if hours > 0:
        return f"{hours}:{minutes:02d}:{seconds:02d}"
    else:
        return f"{minutes}:{seconds:02d}"

def format_views(views):
    if views >= 1000000:
        return f"{views/1000000:.1f}M"
    elif views >= 1000:
        return f"{views/1000:.1f}K"
    else:
        return str(views)

if __name__ == '__main__':
    app.run()
