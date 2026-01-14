import os
import re
from flask import Flask, render_template, request, jsonify
import yt_dlp

app = Flask(__name__)

# دالة للتحقق من الرابط بشكل مرن جداً
def is_valid_youtube_url(url):
    pattern = r'^(https?://)?(www\.)?(youtube\.com|youtu\.be|m\.youtube\.com)/.+$'
    return bool(re.match(pattern, url))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    url = request.form.get('url')
    quality = request.form.get('quality', '720')
    
    if not url or not is_valid_youtube_url(url):
        return jsonify({"error": "الرابط غير صحيح أو غير مدعوم"}), 400

    # إعدادات التحميل مع دعم الكوكيز وتخطي الحظر
    ydl_opts = {
        'cookiefile': 'cookies.txt',  # تأكد من رفع ملف cookies.txt بجانب هذا الملف
        'nocheckcertificate': True,
        'geo_bypass': True,
        'quiet': True,
        'no_warnings': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'format': f"bestvideo[height<={quality}][ext=mp4]+bestaudio[ext=m4a]/best",
        'outtmpl': '%(title)s.%(ext)s',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # استخراج المعلومات أولاً للتأكد من الرابط
            info = ydl.extract_info(url, download=True)
            return jsonify({"message": f"تم تحميل '{info.get('title')}' بنجاح!"})
    except Exception as e:
        return jsonify({"error": f"فشل التحميل: {str(e)}"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    app.run(host='0.0.0.0', port=port)
