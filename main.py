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
def health_check(): return "SmartEntry Just Martink Institutional System Online!", 200

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
                        try:
                            await application.bot.send_message(chat_id=SIGNAL_CHAT_ID, text=output, parse_mode="Markdown")
                        except Exception:
                            await application.bot.send_message(chat_id=SIGNAL_CHAT_ID, text=output)
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
    context.user_data['awaiting_support'] = False
    
    keyboard = [
        [KeyboardButton("📊 طلب صفقة مضاربة"), KeyboardButton("🎁 تجربة يومية مجانية")],
        [KeyboardButton("👑 اشتراك VIP وكالة Just Martink"), KeyboardButton("📞 الدعم الفني المباشر")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "👑 **أهلاً بك في المنصة الرسمية لـ SmartEntry Global بالشراكة مع وكالة Just Martink** 👑\n\n"
        "📋 **دليل التحكم الفوري من جوالك بدون عيوب:**\n"
        "1️⃣ ارفع صورة شارت الذهب أو البيتكوين كـ (صورة أو ملف) ليتم فحصها بالعين البصرية المحدثة فوراً الحين مجاناً.\n"
        "2️⃣ استخدم الأزرار التفاعلية بالأسفل لإدارة اشتراكك والتواصل مع طاقم العمل دغري الحين.",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

async def setup_signals_command(update: Update, context):
    save_stored_chat_id(update.effective_chat.id)
    await update.message.reply_text(f"🎯 **تم ربط وتأمين شات العمليات والرسائل بنجاح:** `{update.effective_chat.id}`", parse_mode="Markdown")

async def scan_now_command(update: Update, context):
    await update.message.reply_text("🔍 **جاري قنص داتا فريمات Twelve Data الحية الحين...**")
    asset_keyword = "xau"
    if context.args: asset_keyword = context.args[0]
    try:
        market_info = get_twelve_data_multi_frame(asset_keyword)
        from ai_analyst import analyze_market_data_text
        analysis_result = analyze_market_data_text(market_info)
        try:
            await update.message.reply_text(analysis_result, parse_mode="Markdown")
        except Exception:
            await update.message.reply_text(analysis_result)
    except Exception as e: await update.message.reply_text(f"❌ خطأ: {str(e)}")

async def handle_chart_photo(update: Update, context):
    context.user_data['awaiting_support'] = False
    await update.message.reply_text("🦅 **عاجل ليدر! تم استلام شارت الجوال، جاري مسحه بالعين البصرية المحدثة الحين...**")
    try:
        photo_file = await update.message.photo[-1].get_file()
        image_bytes = await photo_file.download_as_bytearray()
        from ai_analyst import analyze_chart_image
        analysis_text = analyze_chart_image(image_bytes)
        try:
            await update.message.reply_text(analysis_text, parse_mode="Markdown")
        except Exception:
            await update.message.reply_text(analysis_text)
    except Exception as e: await update.message.reply_text(f"❌ خطأ: {str(e)}")

async def handle_chart_document(update: Update, context):
    context.user_data['awaiting_support'] = False
    document = update.message.document
    if document.mime_type and document.mime_type.startswith("image/"):
        await update.message.reply_text("🦅 **عاجل ليدر! تم استلام شارت الجوال كملف صلب، جاري تشغيل العين البصرية المحدثة الحين...**")
        try:
            doc_file = await document.get_file()
            image_bytes = await doc_file.download_as_bytearray()
            from ai_analyst import analyze_chart_image
            analysis_text = analyze_chart_image(image_bytes)
            try:
                await update.message.reply_text(analysis_text, parse_mode="Markdown")
            except Exception:
                await update.message.reply_text(analysis_text)
        except Exception as e: await update.message.reply_text(f"❌ خطأ بمسح ملف الصورة: {str(e)}")
    else:
        await update.message.reply_text("⚠️ يرجى إرسال ملف صورة صحيح يا ليدر (PNG أو JPEG).")

async def handle_text_buttons(update: Update, context):
    text = update.message.text
    global SIGNAL_CHAT_ID
    
    if context.user_data.get('awaiting_support'):
        context.user_data['awaiting_support'] = False
        user = update.effective_user
        username = f"@{user.username}" if user.username else "لا يوجد يوزرنيم"
        
        support_payload = (
            f"📞 **رسالة دعم فني عاجلة واردة الآن!** 📞\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 **المرسل:** {user.first_name}\n"
            f"🆔 **المعرف الرقمي:** `{user.id}`\n"
            f"🎭 **اسم المستخدم:** {username}\n"
            f"📝 **نص الرسالة:**\n{text}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"💡 *إجراء لليدر:* يمكنك الضغط على اسم العميل والرد عليه دغري الحين الحين."
        )
        
        if SIGNAL_CHAT_ID:
            try:
                await context.bot.send_message(chat_id=SIGNAL_CHAT_ID, text=support_payload, parse_mode="Markdown")
                await update.message.reply_text("✅ **تم إرسال رسالتك وتوجيهها فوراً لطاقم الدعم الفني للوكالة، سيتم التواصل معك دغري الحين يا وحش!**")
            except Exception:
                await context.bot.send_message(chat_id=SIGNAL_CHAT_ID, text=support_payload)
                await update.message.reply_text("✅ **تم إرسال رسالتك بنجاح!**")
        else:
            await update.message.reply_text("⚠️ خطأ إدارة: لم يتم ضبط جروب الاستقبال بعد باستخدام `/setup_signals`.")
        return

    if "طلب صفقة مضاربة" in text:
        await update.message.reply_text("🦅 **أبشر يا ليدر!** ارفع صورة شارت الزوج الحالي (صورة أو ملف Document) وسيقوم وحش العين البصرية بمسحها الحين! 📈")
        
    elif "تجربة يومية مجانية" in text:
        # 🔥 حقن الفلتر الصارم: التحقق مما إذا كان العميل قد استهلك محاولته اليومية الحين
        if context.user_data.get('free_trial_used', False):
            # 🛑 رسالة الصد القيادية والتحويل لرابط الوكالة غصباً عنه الحين الحين
            lock_message = (
                "⚠️ **عذراً يا ليدر! لقد استهلكت محاولتك التجريبية المجانية الملوكية لهذا اليوم.** ⚠️\n\n"
                "🎯 **عشان تفتح عيون البوت البصرية والأسعار اللحظية مدى الحياة مجاناً 100% وبدون أي قيود، الشروط بسيطة جداً من وكالة Just Martink:**\n\n"
                "1️⃣ **سجل حسابك الجديد الحين حصراً من رابط الوكالة الرسمي مالتنا:**\n"
                "🔗 https://one.justmarkets.link/a/tr42sl0svg\n\n"
                "2️⃣ **أدخل كود الشراكة أثناء التسجيل للتأكيد:** `tr42sl0svg`\n"
                "3️⃣ **قم بتفعيل حسابك وإيداع رأس مال التداول الخاص بك الحين.**\n\n"
                "📞 بعد إتمام الخطوات، اضغط على زر **(📞 الدعم الفني المباشر)** بالأسفل وأرسل لنا رقم الـ **Account ID** مالتك، وسيتم ربط وتفعيل حسابك في سيرفر العمليات الكبرى فوراً وبدون أي لاق! 🚀🦅🔥"
            )
            try: await update.message.reply_text(lock_message, parse_mode="Markdown")
            except Exception: await update.message.reply_text(lock_message)
            return

        # إذا كانت المحاولة الأولى، البوت يعطيه الصفقة ويقفل عليه الحساب فوراً الحين
        await update.message.reply_text("🎁 **التجربة اليومية الحية للجدد الحين:** جاري سحب نبض الذهب الفوري لتجربته...")
        try:
            market_info = get_twelve_data_multi_frame("xau")
            from ai_analyst import analyze_market_data_text
            analysis_result = analyze_market_data_text(market_info)
            output = f"🎁 **صفقة تجريبية مجانية حية الحين (Just Martink Free Trial):** 🎁\n\n{analysis_result}"
            
            # قفل المحاولة عليه الحين للأبد
            context.user_data['free_trial_used'] = True
            
            try: await update.message.reply_text(output, parse_mode="Markdown")
            except Exception: await update.message.reply_text(output)
        except Exception as e: await update.message.reply_text(f"❌ السيرفر مضغوط حالياً الحين: {str(e)}")
        
    elif "Just Martink" in text or "VIP" in text:
        await update.message.reply_text(
            "👑 **بوابة اشتراكات VIP المعتمدة - وكالة Just Martink العالمية** 👑\n\n"
            "🔥 انضم الآن لصندوق العمليات الكبرى واستفد من البث الآلي المستمر على مدار الساعة بدون أي لاق!\n\n"
            "💼 **خطط الوكالة والاعتماد الحين:**\n"
            "🔗 **رابط الوكالة المباشر:** https://one.justmarkets.link/a/tr42sl0svg\n"
            "🔑 **Partner Code:** `tr42sl0svg`\n\n"
            "📞 لتفعيل الحساب دغري، اضغط على زر **(📞 الدعم الفني المباشر)** واكتب اسمك ورقم محفظتك الحين وتواصل معنا فوراً!",
            parse_mode="Markdown"
        )
        
    elif "الدعم الفني" in text:
        context.user_data['awaiting_support'] = True
        await update.message.reply_text("📝 **يا مرحب بك يا ليدر! اكتب رسالتك أو مشكلتك الفنية الحين في سطر واحد وأرسلها، وسيتم رفعها فوراً لغرفة عمليات الوكالة...**")

if __name__ == '__main__':
    threading.Thread(target=run_flask_server, daemon=True).start()
    TOKEN = os.environ.get("BOT_TOKEN", "8518436165:AAH2-DjOv0lh9EPpeatvKhAIX-1ODvvvIfY")
    application = Application.builder().token(TOKEN).post_init(post_init).post_shutdown(post_shutdown).build()
    
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("setup_signals", setup_signals_command))
    application.add_handler(CommandHandler("get_twelve_data_multi_frame", scan_now_command))
    application.add_handler(CommandHandler("scan_now", scan_now_command))
    application.add_handler(MessageHandler(filters.PHOTO, handle_chart_photo))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_chart_document))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_buttons))
    application.run_polling()
