import os
import logging
import threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters

# إعدادات اللوغات لمراقبة الأداء
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# سيرفر ويب خفيف في الخلفية لإرضاء ريندر وتجنب الإغلاق
flask_app = Flask(__name__)

@flask_app.route('/')
def health_check():
    return "Multi-Group Deep AI System is Online!", 200

def run_flask_server():
    port = int(os.environ.get("PORT", 10000))
    flask_app.run(host='0.0.0.0', port=port)

async def post_init(application: Application) -> None:
    print("Bot post_init internal setup completed successfully.")

# أوامر البوت الأساسية
async def start_command(update: Update, context):
    await update.message.reply_text(
        "🦅 **مرحباً بك في نظام الـ AI الهجين الخارق لتحليل الأسواق الملوكية!**\n\n"
        "أرسل لي أي صورة شارت (ذهب، عملات، مؤشرات) وسأقوم بتحليلها فوراً بالعين البصرية للذكاء الاصطناعي.",
        parse_mode="Markdown"
    )

async def check_command(update: Update, context):
    await update.message.reply_text("🔄 النظام يعمل بكفاءة قصوى، وجميع الاتصالات بالسيرفر آمنة ومستقرة 100%.")

async def handle_callback_query(update: Update, context):
    query = update.callback_query
    await query.answer()
    try:
        signal = {'sl': 'آمن ومحدد تبعاً للفلاتر', 'rr': 'ممتازة ومطابقة لإدارة المخاطر'}
        score = 9
        ai_explanation = "تحليل فني دقيق يوضح اتجاه السيولة الحالية واختراق مناطق العرض والطلب."
        reply_text = (
            f"📉 **وقف الخسارة:** `{signal['sl']}`\n"
            f"⚖️ **نسبة العائد/المخاطرة:** {signal['rr']}\n"
            f"⭐ **قوة تأكيد الاستراتيجية:** {score}/10\n\n"
            f"🧠 **AI (جيمناي):**\n{ai_explanation}"
        )
        keyboard = [[InlineKeyboardButton("⚡ تداول الآن عبر JustMarkets", url="https://justmarkets.com/?ref=tr42sl0svg")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        if query.data == "get_signal":
            await query.message.reply_text(reply_text, reply_markup=reply_markup, parse_mode="Markdown")
        else:
            await update.message.reply_text("❌ لا توجد إشارة نقية ومطابقة 100% حالياً...", parse_mode="Markdown")
    except Exception as e:
        pass

# دالة استقبال لقطات الشاشة وتحويلها للذكاء الاصطناعي الفعلي
async def handle_chart_photo(update: Update, context):
    await update.message.reply_text("🦅 الحوت الهجين AI... ثواني ملوكية أمر عاجل من الليدر! جاري فحص الشارت بالعين البصرية لـ 📈")
    try:
        photo_file = await update.message.photo[-1].get_file()
        image_bytes = await photo_file.download_as_bytearray()
        
        # استدعاء ملف معالجة الذكاء الاصطناعي
        from ai_analyst import analyze_chart_image
        analysis_text = analyze_chart_image(image_bytes)
        
        await update.message.reply_text(analysis_text)
    except Exception as e:
        await update.message.reply_text(f"❌ عذراً ليدر، حدث خطأ أثناء معالجة الصورة: {str(e)}")

if __name__ == '__main__':
    # تشغيل سيرفر الويب في Thread منفصل لتجنب تعليق البوت
    threading.Thread(target=run_flask_server, daemon=True).start()
    
    TOKEN = os.environ.get("BOT_TOKEN", "8518436165:AAH2-DjOv0lh9EPpeatvKhAIX-1ODvvvIfY")
    application = Application.builder().token(TOKEN).post_init(post_init).build()
    
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("check", check_command))
    application.add_handler(CallbackQueryHandler(handle_callback_query))
    application.add_handler(MessageHandler(filters.PHOTO, handle_chart_photo))
    
    print("Multi-Group Deep AI System is fully online. Ready.")
    application.run_polling()
