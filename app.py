from flask import Flask, request, jsonify, send_file, after_this_request
from flask_cors import CORS
import yt_dlp
import os
import time
import re



app = Flask(__name__)
audio_folder = 'audios'
currentworkingaudios = os.getcwd() + '/' + audio_folder
app.config['UPLOAD_FOLDER'] = currentworkingaudios

CORS(app, resources={r"/api/*": {"origins": ["http://localhost:3000", "http://example.com"]}})

def sanitize_filename(filename):
    # Replace any character that is not alphanumeric, dash, underscore, or period with an underscore
    sanitized_filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
    return sanitized_filename


def get_video_title(url):
    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'force_generic_extractor': True,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        video_title = info_dict.get('title', None)
        return video_title


def download_audio(url, newTitle, output_path=audio_folder):
    try:

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'{output_path}/{newTitle}.%(ext)s',
            'quiet': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }



        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            dl = ydl.download([url])
            info_dict = ydl.extract_info(url, download=True)  # Download the video
            title = info_dict.get('title', None)  # Retrieve the title
            ext = info_dict.get('ext', None)  # Retrieve the extension
            print(title, ext)
        print("Download completed")
        return f'{output_path}/{newTitle}.mp3'
    except Exception as e:
        print(f"An error occurred: {e}")


def list_files(startpath):
    for root, dirs, files in os.walk(startpath):
        level = root.replace(startpath, '').count(os.sep)
        indent = ' ' * 4 * (level)
        print(f'{indent}{os.path.basename(root)}/')
        subindent = ' ' * 4 * (level + 1)
        for file in files:
            print(f'{subindent}{file}')



@app.route('/api/data', methods=['POST'])
def receive_data():
    data = request.json
    videoTitle = get_video_title(data['url'])
    new_title = sanitize_filename(videoTitle)
    outputPath = download_audio( data['url'], new_title )


    if os.path.isfile(outputPath):
        @after_this_request
        def remove_file( response ):
            try:
                os.remove(outputPath)
            except Exception as e:
                app.logger.error(f'Error removing file: {e}')
            return response
        return send_file(outputPath, mimetype='audio/mpeg')
    else:
        return "File not found", 404

if __name__ == '__main__':
    app.run(debug=True)