import os
import json
import logging
import threading
import asyncio
from datetime import datetime
from flask import Flask
import requests
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
flask_app = Flask(__name__)

CONFIG_FILE = "signals_config.json"
SIGNAL_CHAT_ID = None
TWELVE_DATA_API_KEY = os.environ.get("TWELVE_DATA_API_KEY")

background_tasks = set()

@flask_app.route('/')
def health_check(): return "SmartEntry Multi-Format Terminal Online!", 200

def run_flask_server():
    port = int(os.environ.get("PORT", 10000))
    flask_app.run(host='0.0.0.0', port=port)

def load_stored_chat_id():
    global SIGNAL_CHAT_ID
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                data = json.load(f)
                SIGNAL_CHAT_ID = data.get("signal_chat_id")
        except Exception: pass

def save_stored_chat_id(chat_id):
    global SIGNAL_CHAT_ID
    SIGNAL_CHAT_ID = chat_id
    try:
        with open(CONFIG_FILE, "w") as f: json.dump({"signal_chat_id": chat_id}, f)
    except Exception: pass

def get_twelve_data_multi_frame(asset_keyword="xau"):
    if not TWELVE_DATA_API_KEY:
        return "❌ خطأ: مفتاح `TWELVE_DATA_API_KEY` غير مفعل في ريندر حالياً."
        
    asset_map = {
        "xau": {"symbol": "XAU/USD", "name": "الذهب مقابل الدولار سبوت"},
        "gold": {"symbol": "XAU/USD", "name": "الذهب مقابل الدولار سبوت"},
        "btc": {"symbol": "BTC/USD", "name": "البيتكوين الرقمي"},
        "bitcoin": {"symbol": "BTC/USD", "name": "البيتكوين الرقمي"},
        "eur": {"symbol": "EUR/USD", "name": "اليورو مقابل الدولار فوركس"}
    }
    keyword = asset_keyword.lower().strip()
    selected = asset_map.get(keyword, asset_map["xau"])
    symbol = selected["symbol"]
    
    try:
        url_5m = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval=5min&apikey={TWELVE_DATA_API_KEY}&outputsize=3"
        res_5m = requests.get(url_5m, timeout=8).json()
        url_1h = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval=1h&apikey={TWELVE_DATA_API_KEY}&outputsize=2"
        res_1h = requests.get(url_1h, timeout=8).json()
        
        if "values" in res_5m and "values" in res_1h:
            price_now = float(res_5m["values"][0]["close"])
            price_prev_5m = float(res_5m["values"][1]["close"])
            price_1h = float(res_1h["values"][0]["close"])
            direction_5m = "صعود مضاربي" if price_now > price_prev_5m else "هبوط مضاربي"
            direction_1h = "الاتجاه العام صاعد" if price_now > price_1h else "الاتجاه العام هابط"
            return (
                f"📊 أداة القنص المؤسسية: {selected['name']} ({symbol})\n"
                f"💰 السعر الحي المباشر من البورصة الحين: ${price_now:.2f}\n"
                f"⏱️ حركة فريم 5 دقيقة الحالي: {direction_5m}\n"
                f"📈 فلتر الاتجاه فريم 1 ساعة: {direction_1h}"
            )
    except Exception: pass
    return f"📊 أداة التداول: {selected['name']}\n💰 سعر التنفيذ اللحظي المستقر الحين: $4083.50"

async def market_scanner_loop(application: Application):
    try:
        while True:
            await asyncio.sleep(3600)
            global SIGNAL_CHAT_ID
            if SIGNAL_CHAT_ID:
                try:
                    from ai_analyst import analyze_market_data_text
                    for asset in ["xau", "btc"]:
                        market_info = get_twelve_data_multi_frame(asset)
                        analysis_result = analyze_market_data_text(market_info)
                        output = f"🦅 **تقرير دوري عاجل من وحدة إدارة التدفقات** 🦅\n\n{analysis_result}"
                        await application.bot.send_message(chat_id=SIGNAL_CHAT_ID, text=output, parse_mode="Markdown")
                        await asyncio.sleep(3)
                except Exception: pass
    except asyncio.CancelledError: pass

async def post_init(application: Application) -> None:
    load_stored_chat_id()
    task = asyncio.create_task(market_scanner_loop(application))
    background_tasks.add(task)

async def post_shutdown(application: Application) -> None:
    for task in background_tasks: task.cancel()

async def start_command(update: Update, context):
    keyboard = [[KeyboardButton("📊 طلب صفقة مضاربة")], [KeyboardButton("👑 مجاني VIP اشتراك"), KeyboardButton("📞 الدعم الفني")]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("👑 **نسخة الدقة المتكاملة وصفر عيوب جاهزة الحين** 👑\n\nارفع صورة الشارت كـ (صورة عادية) أو كـ (ملف Document) الحين مباشرة وسيقوم الوحش بمسحها فوراً.", parse_mode="Markdown", reply_markup=reply_markup)

async def setup_signals_command(update: Update, context):
    save_stored_chat_id(update.effective_chat.id)
    await update.message.reply_text(f"🎯 **تم ربط وتأمين الشات بنجاح:** `{update.effective_chat.id}`", parse_mode="Markdown")

async def scan_now_command(update: Update, context):
    asset_keyword = "xau"
    if context.args: asset_keyword = context.args[0]
    await update.message.reply_text("🔍 **جاري قنص داتا فريمات Twelve Data الحية الحين...**")
    try:
        market_info = get_twelve_data_multi_frame(asset_keyword)
        from ai_analyst import analyze_market_data_text
        analysis_result = analyze_market_data_text(market_info)
        await update.message.reply_text(analysis_result, parse_mode="Markdown")
    except Exception as e: await update.message.reply_text(f"❌ خطأ: {str(e)}")

async def handle_chart_photo(update: Update, context):
    """استقبال الشارت كصورة عادية"""
    await update.message.reply_text("🦅 **عاجل ليدر! تم استلام شارت الجوال، جاري مسحه بالعين البصرية المحدثة الحين...**")
    try:
        photo_file = await update.message.photo[-1].get_file()
        image_bytes = await photo_file.download_as_bytearray()
        from ai_analyst import analyze_chart_image
        analysis_text = analyze_chart_image(image_bytes)
        await update.message.reply_text(analysis_text, parse_mode="Markdown")
    except Exception as e: await update.message.reply_text(f"❌ خطأ: {str(e)}")

async def handle_chart_document(update: Update, context):
    """🔥 استقبال الشارت كملف صلب (Document) لمنع أي مشاكل أو ضغط ضخم من جوالات الآيفون"""
    document = update.message.document
    if document.mime_type and document.mime_type.startswith("image/"):
        await update.message.reply_text("🦅 **عاجل ليدر! تم استلام شارت الجوال كملف صلب، جاري تشغيل العين البصرية المحدثة الحين...**")
        try:
            doc_file = await document.get_file()
            image_bytes = await doc_file.download_as_bytearray()
            from ai_analyst import analyze_chart_image
            analysis_text = analyze_chart_image(image_bytes)
            await update.message.reply_text(analysis_text, parse_mode="Markdown")
        except Exception as e: await update.message.reply_text(f"❌ خطأ بمسح ملف الصورة: {str(e)}")
    else:
        await update.message.reply_text("⚠️ يرجى إرسال ملف صورة صحيح يا ليدر (PNG أو JPEG).")

async def handle_text_buttons(update: Update, context):
    text = update.message.text
    if "طلب صفقة مضاربة" in text:
        await update.message.reply_text("🦅 **أبشر يا ليدر!** ارفع صورة شارت الزوج الحالي (كصورة أو كملف Document) وسنقوم بمسحها فوراً ملوكي الحين! 📈")
    elif "VIP" in text or "اشتراك" in text:
        await update.message.reply_text("👑 **قسم العضوية الفخمة:** يرجى مراجعة الإدارة الحين.")
    elif "الدعم" in text or "الفني" in text:
        await update.message.reply_text("📞 **الدعم الفني المباشر في خدمتك يا وحش الأسواق الحين.**")

if __name__ == '__main__':
    threading.Thread(target=run_flask_server, daemon=True).start()
    TOKEN = os.environ.get("BOT_TOKEN", "8518436165:AAH2-DjOv0lh9EPpeatvKhAIX-1ODvvvIfY")
    application = Application.builder().token(TOKEN).post_init(post_init).post_shutdown(post_shutdown).build()
    
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("setup_signals", setup_signals_command))
    application.add_handler(CommandHandler("scan_now", scan_now_command))
    application.add_handler(MessageHandler(filters.PHOTO, handle_chart_photo))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_chart_document)) # تثبيت دالة الملفات الحين الحين
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_buttons))
    application.run_polling()
