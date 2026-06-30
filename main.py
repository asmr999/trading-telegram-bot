# main.py
import keep_alive
import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import config
import database
import analyzer

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def auto_signal_scheduler(application: Application):
    print("⏰ تم تشغيل رادار الفحص التلقائي كل 30 دقيقة...")
    await asyncio.sleep(20)
    while True:
        try:
            for asset in ["XAUUSD", "EURUSD", "BTCUSDT"]:
                df = analyzer.get_live_data(asset, "30m")
                signal, score = analyzer.calculate_signals(df)
                if signal and score >= 6:
                    admin_text = f"🚨 طلب فحص وموافقة على صفقة مجانية (كل 30 دقيقة) 🚨\n\n" \
                                 f"📊 الزوج: {asset}\n⏱️ الفريم: 30 دقيقة\n🎯 الاتجاه: {signal['direction']}\n" \
                                 f"💵 سعر الدخول: {signal['entry']}\n💰 جني الأرباح: {signal['tp']}\n" \
                                 f"🛑 وقف الخسارة: {signal['sl']}\n⚖️ قوة التأكيد: {score}/10 مؤشرات"
                    keyboard = [[InlineKeyboardButton("✅ موافقة ونشر بالجروب العام", callback_data=f"sendfree_{asset}"),
                                 InlineKeyboardButton("❌ رفض وإلغاء الصفقة", callback_data="rejectfree")]]
                    await application.bot.send_message(chat_id=config.ADMIN_GROUP_ID, text=admin_text, reply_markup=InlineKeyboardMarkup(keyboard))
                    break
        except Exception as e: print(f"تنبيه المجدول: {e}")
        await asyncio.sleep(1800)

async def post_init(application: Application):
    asyncio.create_task(auto_signal_scheduler(application))

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    database.add_user(user.id, user.username)
    keyboard = [['📊 طلب صفقة مضاربة'], ['👑 اشتراك VIP مجاني', '📞 الدعم الفني']]
    await update.message.reply_text(f"أهلاً بك يا {user.first_name} في رادار التحليل العشري الخارق! 🚀", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

async def handle_text_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text, user_id, username = update.message.text, update.effective_user.id, (update.effective_user.username or "بدون معرف")

    if context.user_data.get('awaiting_jm_id'):
        context.user_data['awaiting_jm_id'] = False
        if not text.isdigit():
            await update.message.reply_text("⚠️ خطأ! أدخل أرقام فقط.")
            return
        database.update_justmarkets_id(user_id, text)
        await update.message.reply_text("✅ تم حفظ الحساب! جاري تدقيقه من قبل الإدارة لتفعيل الـ VIP.")
        admin_alert = f"📥 طلب تسجيل حساب JustMarkets جديد 📥\n\n👤 المشترك: @{username}\n🆔 الآيدي: {user_id}\n🔢 رقم الحساب: {text}\n\n⚙️ للتفعيل بنقرة واحدة:\n/vip {user_id}"
        await context.bot.send_message(chat_id=config.ADMIN_GROUP_ID, text=admin_alert)
        return

    if context.user_data.get('awaiting_support_msg'):
        context.user_data['awaiting_support_msg'] = False
        await context.bot.send_message(chat_id=config.ADMIN_GROUP_ID, text=f"📩 دعم من @{username}:\n{text}")
        await update.message.reply_text("✅ تم إرسال رسالتك بنجاح للإدارة.")
        return

    if text == '📊 طلب صفقة مضاربة':
        keyboard = [[InlineKeyboardButton("🏆 הذهب (XAU/USD)", callback_data='asset_XAUUSD')],
                    [InlineKeyboardButton("EUR/USD (فوركس)", callback_data='asset_EURUSD'), InlineKeyboardButton("BTC/USDT (كريبتو)", callback_data='asset_BTCUSDT')]]
        await update.message.reply_text("إختر الأصل المالي:", reply_markup=InlineKeyboardMarkup(keyboard))
    elif text == '👑 اشتراك VIP مجاني':
        keyboard = [
            [InlineKeyboardButton("🔗 1. فتح حساب في JustMarkets وبدء التداول", url=config.JUSTMARKETS_REF_LINK)],
            [InlineKeyboardButton('📝 2. ربط وتوثيق رقم حسابك بالبوت', callback_data='register')]
        ]
