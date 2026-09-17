FROM python:3.10-slim

# 1. FFmpeg တပ်ဆင်ခြင်း (YouTube ဖိုင်များကို MP3/MP4 ပြောင်းရန် မဖြစ်မနေ လိုအပ်ပါသည်)
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 2. Python Packages များ တပ်ဆင်ခြင်း
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3. Project ဖိုင်အားလုံးကို Container ထဲသို့ ကူးယူခြင်း
COPY . .

EXPOSE 10000

# 4. Gunicorn ဖြင့် Production Server Run ခြင်း
# (-t 300 သည် ဖိုင်ကြီးများ ဒေါင်းလုဒ်ဆွဲစဉ် Server မရပ်သွားစေရန် ၅ မိနစ် အချိန်ပေးထားခြင်း ဖြစ်ပါသည်)
CMD ["gunicorn", "-b", "0.0.0.0:10000", "-w", "2", "-t", "300", "app:app"]
