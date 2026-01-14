FROM python:3.10-slim

# تثبيت FFmpeg لدمج الصوت والفيديو
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# نسخ الملفات وتثبيت المكتبات
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# نسخ كامل المشروع (بما في ذلك المجلدات الجديدة static و templates)
COPY . .

ENV PORT=7860
EXPOSE 7860

# تشغيل السيرفر
CMD ["gunicorn", "--bind", "0.0.0.0:7860", "app:app"]
