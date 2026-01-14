import os
from flask import Flask, render_template, request, jsonify
import yt_dlp

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    # استلام البيانات بصيغة JSON لضمان التوافق مع JavaScript
    data = request.get_json()
    if not data:
        return jsonify({"error": "لم يتم استلام بيانات"}), 400
        
    url = data.get('url')
    quality = data.get('quality', '720')
    
    if not url:
        return jsonify({"error": "الرجاء إدخال رابط الفيديو"}), 400

    ydl_opts = {
        'cookiefile': 'cookies.txt', # ملف الكوكيز ضروري لتجاوز حظر يوتيوب
        'nocheckcertificate': True,
        'geo_bypass': True,
        'quiet': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'format': f"bestvideo[height<={quality}][ext=mp4]+bestaudio[ext=m4a]/best",
        'outtmpl': '%(title)s.%(ext)s',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return jsonify({"message": "تم التحميل بنجاح على السيرفر!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    app.run(host='0.0.0.0', port=port)
