import yt_dlp
from flask import Flask, request, send_file, jsonify
import os


def download_audio(url, output_path='.'):
    try:
        print()
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'{output_path}/%(title)s.%(ext)s',
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
        return f'{output_path}/{title}.mp3'
    except Exception as e:
        print(f"An error occurred: {e}")

# # Example usage
# url = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'  # Replace with your YouTube video URL
# download_audio(url)



app = Flask(__name__)



@app.route('/')
def home():
    return "Welcome to the Flask server!"


@app.route('/songurl', methods=['GET'])
def songurlGet():
    return

@app.route('/songurl', methods=['POST'])
def songurl():
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({"error": "Please provide a valid URL in JSON format"}), 400

    print(data)
    audio_file_path = download_audio(data['url'])
    
    return send_file(audio_file_path, as_attachment=True, mimetype='audio/mpeg')

if __name__ == '__main__':
    app.run(port=8080)