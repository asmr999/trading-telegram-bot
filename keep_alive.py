from flask import Flask
from threading import Thread
import os

app = Flask('')

@app.route('/')
def home():
    return "Bot is running perfectly alive!"

def run_server():
    # لقط البورت السري الخاص بـ Render ومنع الإغلاق المبكر نهائياً
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# بدء تشغيل السيرفر في خلفية النظام فوراً بمجرد الاستدعاء
t = Thread(target=run_server)
t.daemon = True
t.start()
print("Render Web Server successfully bound to port.")
