from flask import Flask
from threading import Thread
import os
import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes

# 1. تشغيل سيرفر الويب لمنصة Render فوراً لمنع الإغلاق المبكر
app = Flask('')
@app.route('/')
def home(): 
    return "Bot is Alive and Running!"
def run(): 
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
Thread(target=run, daemon=True).start()

# 2. استيراد الملفات الخارجية الخاصة بالبوت
import config
import database
import analyzer

# 3. مبرمج ومجدول الفحص التلقائي للمؤشرات الفنية
async def auto_signal_scheduler(application: Application):
    print("... تم تشغيل رادار الفحص التلقائي كل 30 دقيقة ...")
    await asyncio.sleep(20)
    while True:
        try:
            for asset in ["XAUUSD", "EURUSD", "BTCUSDT"]:
                df = analyzer.get_live_data(asset, "30m")
                signal, score = analyzer.calculate_signals(df)
                if signal and score >= 6:
                    admin_text = f"🚨 \n\n\n 📊 طلب فحص وموافقة على صفقة مجانية (كل 30 دقيقة) \n\n" \
                                 f"🔹 الأصول: {asset}\n" \
                                 f"📈 الاتجاه: {signal['direction']}\n" \
                                 f"🟢 سعر الدخول: {signal['entry']}\n" \
                                 f"🎯 جني الأرباح: {signal['tp']}\n" \
                                 f"🛑 وقف الخسارة: {signal['sl']}\n" \
                                 f"📊 مؤشرات: {score}/10 \n\n"
                    keyboard = [[InlineKeyboardButton(" موافقة ونشر بالجروب العام ", callback_data=f"sendfree_{asset}"),
                                 InlineKeyboardButton(" رفض وإلغاء الصفقة ❌ ", callback_data="rejectfree")]]
                    await application.bot.send_message(chat_id=config.ADMIN_GROUP_ID, text=admin_text, reply_markup=InlineKeyboardMarkup(keyboard))
        except Exception as e:
            print(f"تنبيه المجدول: {e}")
        await asyncio.sleep(1800)

async def post_init(application: Application):
    asyncio.create_task(auto_signal_scheduler(application))

# 4. أمر البداية /start ترحيب وتجهيز الكيبورد الرئيسي
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    database.add_user(user.id, user.username)
    keyboard = [['📊 طلب صفقة مضاربة', '👑 مجاني VIP اشتراك'], ['📞 الدعم الفني']]
    await update.message.reply_text(
        f"أهلاً بك يا {user.first_name} في رادار التحليل الفني الخارق! 🚀", 
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

# 5. معالج الرسائل النصية وضغطات الأزرار العادية
async def handle_text_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id
    username = update.effective_user.username or "بدون معرف"

    if context.user_data.get('awaiting_jm_id'):
        context.user_data['awaiting_jm_id'] = False
        if not text.isdigit():
            await update.message.reply_text("⚠️ خطأ! أدخل أرقام فقط.")
            return
        database.update_justmarkets_id(user_id, text)
        await update.message.reply_text("🎉 تم حفظ الحساب! جاري تدقيقه من قبل الإدارة لتفعيل الـ VIP.")
        admin_alert = f"👤 مشترك @{username} الأي دي: {user_id} \n رقم الحساب {text} \n\n طلب تسجيل حساب JustMarkets جديد"
        await context.bot.send_message(chat_id=config.ADMIN_GROUP_ID, text=admin_alert)
        return

    if context.user_data.get('awaiting_support_msg'):
        context.user_data['awaiting_support_msg'] = False
        await context.bot.send_message(chat_id=config.ADMIN_GROUP_ID, text=f"✉️ دعم من @{username}:\n{text}")
        await update.message.reply_text("✅ تم إرسال رسالتك بنجاح للإدارة.")
        return

    if text == '📊 طلب صفقة مضاربة':
        keyboard = [
            [InlineKeyboardButton("🏆 ذهب (XAU/USD)", callback_data='asset_XAUUSD')],
            [InlineKeyboardButton("EUR/USD (فوركس)", callback_data='asset_EURUSD'), InlineKeyboardButton("BTC/USDT (كريبتو)", callback_data='asset_BTCUSDT')]
        ]
        await update.message.reply_text("📊 إختر الأصل المالي:", reply_markup=InlineKeyboardMarkup(keyboard))
    elif text == '👑 مجاني VIP اشتراك':
        keyboard = [
            [InlineKeyboardButton("🔗 1. فتح حساب في JustMarkets وبدء التداول", url=config.JUSTMARKETS_REF_LINK)],
            [InlineKeyboardButton("📝 2. ربط وتوثيق رقم حسابك بالبوت", callback_data='register')]
        ]
        await update.message.reply_text("للاشتراك المجاني:", reply_markup=InlineKeyboardMarkup(keyboard))
    elif text == '📞 الدعم الفني':
        context.user_data['awaiting_support_msg'] = True
        await update.message.reply_text("📥 أرسل رسالتك الآن وسيتم تحويلها مباشرة للدعم الفني.")

# 6. المحرك الأساسي لتشغيل واستماع البوت اللانهائي الحقيقي
if __name__ == '__main__':
    TOKEN = "8518436165:AAH2-DjOv0lh9EPpeatvKhAIX-l0DvvvIfY"
    application = Application.builder().token(TOKEN).post_init(post_init).build()
    
    # تسجيل المستمعين للأوامر والرسائل
    application.add_handler(CommandHandler("start", start_command))
    from telegram.ext import filters
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_messages))
    
    print("Bot successfully initialized and listening for live updates...")
    application.run_polling()
