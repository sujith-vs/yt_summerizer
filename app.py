#imports
import yt_dlp
import os
import requests
from yt_dlp.utils import sanitize_filename
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os

load_dotenv()

API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
headers = {"Authorization": f"Bearer {os.getenv('HF_TOKEN')}"}
# Flask setup
app = Flask(__name__)
CORS(app)

# Function to get captions
def get_captions(youtube_url):
    output_path = './temp/'
    os.makedirs(output_path, exist_ok=True)
    ydl_opts = {
        'skip_download': True,
        'writesubtitles': True,
        'writeautomaticsub': True,
        'subtitleslangs': ['en'],
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s')
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(youtube_url, download=True)
    return result.get('title', None)

# Function to convert vtt to text
def vtt_to_text(vtt_file):
    text = ""
    with open(vtt_file, "r", encoding="utf-8") as f:
        for line in f:
            if "-->" in line or line.strip().isdigit() or line.strip() == "":
                continue
            text += line.strip() + " "
    return text

# Function to summarize text
def summarize_large_text(text, max_chunk=1000):
    summaries = []
    for i in range(0, len(text), max_chunk):
        chunk = text[i:i+max_chunk]
        payload = {"inputs": chunk}
        response = requests.post(API_URL, headers=headers, json=payload)
        result = response.json()
        if isinstance(result, list):
            summaries.append(result[0]['summary_text'])
    return " ".join(summaries)

# Flask API Route
@app.route('/summarize', methods=['POST'])
def summarize_video():
    data = request.get_json()
    youtube_url = data.get('url')

    if not youtube_url:
        return jsonify({'error': 'URL is missing'}), 400

    title = get_captions(youtube_url)
    safe_title = sanitize_filename(title)
    vtt_path = f'./temp/{safe_title}.en.vtt'

    if not os.path.exists(vtt_path):
        return jsonify({'error': 'Captions not found'})

    text = vtt_to_text(vtt_path)
    summary = summarize_large_text(text)
    os.remove(vtt_path)

    return jsonify({'summary': summary})

# Run Flask server
if __name__ == '__main__':
    app.run()