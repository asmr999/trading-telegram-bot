from flask import Flask
from threading import Thread
import os

app = Flask('')

@app.route('/')
def home():
    return "Bot is running perfectly!"

def run():
    # الحل الجذري: إجبار السيرفر على قراءة البورت الخاص بـ Render ومنع الإغلاق المبكر
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()
