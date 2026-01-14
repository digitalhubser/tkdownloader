# استخدام نسخة بايثون رسمية خفيفة
FROM python:3.9-slim

# تحديث النظام وتثبيت FFmpeg (النسخة المتوافقة مع السيرفر)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# تحديد مجلد العمل داخل السيرفر
WORKDIR /app

# نسخ ملف المكتبات وتثبيتها
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# نسخ كل ملفات مشروعك إلى السيرفر (app.py والمجلدات)
COPY . .

# إعطاء صلاحيات التشغيل (احتياطاً)
RUN chmod +x app.py

# المنفذ الذي سيعمل عليه السيرفر (7860 لـ Hugging Face و 8080 لـ Render)
# ملاحظة: تأكد أن المنفذ في app.py يطابق هذا المنفذ
EXPOSE 7860

# أمر تشغيل التطبيق باستخدام gunicorn (أفضل للسيرفرات)
# إذا لم تكن تستخدم gunicorn، استبدله بـ ["python", "app.py"]
CMD ["python", "app.py"]
