import os
import re
from flask import Flask, render_template, request, jsonify
import yt_dlp

app = Flask(__name__)

# دالة ذكية للتحقق من أن الرابط يخص يوتيوب فعلاً
def is_valid_youtube_url(url):
    if not url:
        return False
    youtube_regex = (
        r'(https?://)?(www\.)?'
        '(youtube|youtu|youtube-nocookie)\.(com|be)/'
        '(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
    )
    return re.match(youtube_regex, url) is not None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    # استلام الرابط من الفورم - تأكد أن name="url" في ملف index.html
    url = request.form.get('url', '').strip()
    quality = request.form.get('quality', '720')

    if not url or not is_valid_youtube_url(url):
        return jsonify({"error": "عذراً، الرابط غير صحيح. تأكد من نسخ رابط فيديو يوتيوب"}), 400

    # إعدادات yt-dlp الاحترافية
    ydl_opts = {
        'cookiefile': 'cookies.txt',  # استخدام الملف الذي رفعته
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
            # استخراج البيانات والتحميل
            info = ydl.extract_info(url, download=True)
            video_title = info.get('title', 'فيديو غير معروف')
            return jsonify({"message": f"تم بنجاح تحميل: {video_title}"})
    except Exception as e:
        # إذا فشل بسبب الكوكيز أو غيره، سنعرف السبب من هنا
        error_msg = str(e)
        if "sign in" in error_msg.lower():
            return jsonify({"error": "يوتيوب يطلب تحديث ملف الكوكيز. يرجى استخراج ملف جديد."}), 403
        return jsonify({"error": f"حدث خطأ أثناء التحميل: {error_msg}"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    app.run(host='0.0.0.0', port=port)
