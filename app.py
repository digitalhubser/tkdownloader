import os
import threading
import uuid
import shutil
import time
from flask import Flask, render_template, request, jsonify, send_from_directory
import yt_dlp

app = Flask(__name__)

# الإعدادات الأساسية
DOWNLOAD_FOLDER = 'server_temp'
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

# مخزن المهام (Status Store)
tasks = {}


def reset_storage():
    """مسح المجلدات القديمة عند بدء التشغيل"""
    if os.path.exists(DOWNLOAD_FOLDER):
        shutil.rmtree(DOWNLOAD_FOLDER)
    os.makedirs(DOWNLOAD_FOLDER)

def cleanup_task(task_id, delay=300):
    """مسح الملفات بعد فترة (5 دقائق لضمان تحميل الملفات المنفردة)"""
    time.sleep(delay)
    folder_path = os.path.join(DOWNLOAD_FOLDER, task_id)
    zip_path = os.path.join(DOWNLOAD_FOLDER, f"{task_id}.zip")
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)
    if os.path.exists(zip_path):
        os.remove(zip_path)


def download_task(url, quality, task_id):
    folder_path = os.path.join(DOWNLOAD_FOLDER, task_id)
    os.makedirs(folder_path, exist_ok=True)

    # ydl_opts = {
    #     'format': f"bestvideo[height<={quality}][ext=mp4]+bestaudio[ext=m4a]/best",
    #     'outtmpl': os.path.join(folder_path, '%(title)s.%(ext)s'),
    #     'playlistend': 50, # صمام أمان لعدد الفيديوهات
    #     'nocheckcertificate': True,
    #     'quiet': True,
    # }
   ydl_opts = {
        'cookiefile': 'cookies.txt',  # السطر الأهم لتجاوز حظر البوت
        'nocheckcertificate': True,
        'geo_bypass': True,
        'quiet': True,
       'playlistend': 50,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'format': f"bestvideo[height<={quality}][ext=mp4]+bestaudio[ext=m4a]/best",
        'outtmpl': os.path.join(folder_path, '%(title)s.%(ext)s'),
    }
    

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        # محاولة الضغط (المرحلة الحساسة)
        zip_path = os.path.join(DOWNLOAD_FOLDER, f"{task_id}.zip")
        try:
            # نقوم بالضغط
            shutil.make_archive(zip_path.replace('.zip', ''), 'zip', folder_path)
            tasks[task_id]['status'] = 'finished'
            tasks[task_id]['file'] = f"{task_id}.zip"
        except Exception as zip_error:
            print(f"Zip Failed: {zip_error}")
            # الحل البديل: إرسال أسماء الملفات المحملة
            files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
            tasks[task_id]['status'] = 'fallback'
            tasks[task_id]['files'] = files

    except Exception as e:
        tasks[task_id]['status'] = 'failed'
        tasks[task_id]['error'] = str(e)
    
    # تشغيل التنظيف التلقائي
    threading.Thread(target=cleanup_task, args=(task_id,)).start()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def start_download():
    url = request.json.get('url')
    quality = request.json.get('quality', '720')
    task_id = str(uuid.uuid4())
    tasks[task_id] = {'status': 'downloading', 'progress': 0}
    
    threading.Thread(target=download_task, args=(url, quality, task_id)).start()
    return jsonify({'task_id': task_id})

@app.route('/status/<task_id>')
def get_status(task_id):
    return jsonify(tasks.get(task_id, {'status': 'not_found'}))

@app.route('/download_file/<filename>')
def download_file(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename, as_attachment=True)

@app.route('/download_single/<task_id>/<filename>')
def download_single(task_id, filename):
    directory = os.path.join(DOWNLOAD_FOLDER, task_id)
    return send_from_directory(directory, filename, as_attachment=True)


if __name__ == '__main__':
    reset_storage()
    app.run(host='0.0.0.0', port=7860)


