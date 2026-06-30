from flask import Flask
from threading import Thread
import os
import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, CallbackQueryHandler

# تشغيل سيرفر الويب لمنصة Render لضمان عمل البوت 24 ساعة بدون نوم
app = Flask('')
@app.route('/')
def home(): 
    return "Official High-Precision Multi-Group System is Active!"
def run(): 
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
Thread(target=run, daemon=True).start()

import config
import database
import analyzer

# 🎯 ربط المعرفات الرسمية الخاصة بجروباتك مباشرة بالسيستم لحقن الصفقات
ADMIN_GROUP_ID = -1003310992331
VIP_GROUP_ID = -1004372200363

# مخزن مؤقت ذكي لحفظ الصفقات وتجنب مشكلة حد الـ 64 بايت في أزرار تيليجرام
PENDING_SIGNALS = {}
SIGNAL_ID_COUNTER = 0
FREE_TRIAL_COUNTER = {}

# مجدول الفحص التلقائي للإدارة كل 5 دقائق
async def auto_signal_scheduler(application: Application):
    global SIGNAL_ID_COUNTER
    print("... تم إطلاق رادار الفحص التلقائي للإدارة كل 5 دقائق ...")
    await asyncio.sleep(10)
    while True:
        try:
            for asset in ["XAUUSD", "EURUSD", "BTCUSDT"]:
                df = analyzer.get_live_data(asset, "30m")
                signal, score = analyzer.calculate_signals(df)
                
                if signal and score >= 8:
                    SIGNAL_ID_COUNTER += 1
                    PENDING_SIGNALS[SIGNAL_ID_COUNTER] = {
                        "asset": asset,
                        "type": signal['type'],
                        "entry": signal['entry'],
                        "tp": signal['tp'],
                        "sl": signal['sl']
                    }
                    
                    admin_text = f"💎 **رادار الإدارة المباشر (فرصة جديدة)** 💎\n\n" \
                                 f"📊 **الأصل المالي:** {asset}\n" \
                                 f"⚙️ **نوع الإشارة:** {signal['type']}\n" \
                                 f" ---------------------------------- \n" \
                                 f"🟢 **سعر الدخول المقترح:** {signal['entry']}\n" \
                                 f"🎯 **الهدف (TP):** {signal['tp']}\n" \
                                 f"🛑 **وقف الخسارة (SL):** {signal['sl']}\n" \
                                 f"⭐ **قوة دقة الفلتر الفني:** {score}/10\n\n" \
                                 f"👇 اضغط على قرارك لحقن الصفقة رسمياً في جروب الـ VIP:"
                                 
                    keyboard = [[
                        InlineKeyboardButton("✅ موافقة ونشر بالـ VIP", callback_data=f"vip_pay_{SIGNAL_ID_COUNTER}"),
                        InlineKeyboardButton("❌ إلغاء واستبعاد", callback_data=f"vip_rej_{SIGNAL_ID_COUNTER}")
                    ]]
                    await application.bot.send_message(chat_id=ADMIN_GROUP_ID, text=admin_text, reply_markup=InlineKeyboardMarkup(keyboard))
        except Exception as e:
            print(f"خطأ في مجدول الإدارة: {e}")
        await asyncio.sleep(300)

async def post_init(application: Application):
    asyncio.create_task(auto_signal_scheduler(application))

# ميزة الطلب الفوري للّيدر (تكتب في جروب الإدارة /check XAUUSD)
async def check_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global SIGNAL_ID_COUNTER
    chat_id = update.effective_chat.id
    if chat_id != ADMIN_GROUP_ID:
        return 
        
    if not context.args:
        await update.message.reply_text("⚠️ يرجى كتابة اسم الأصل المالي مع الأمر، مثال:\n`/check XAUUSD`")
        return
        
    asset = context.args[0].upper()
    await update.message.reply_text(f"🚀 أمر فوري من اللّيدر! جاري فحص {asset} الحين بقوة 10 مؤشرات داخلية صلبة...")
    
    try:
        df = analyzer.get_live_data(asset, "30m")
        signal, score = analyzer.calculate_signals(df)
        if signal:
            SIGNAL_ID_COUNTER += 1
            PENDING_SIGNALS[SIGNAL_ID_COUNTER] = {
                "asset": asset,
                "type": signal['type'],
                "entry": signal['entry'],
                "tp": signal['tp'],
                "sl": signal['sl']
            }
            
            admin_text = f"⚡ **تحليل فوري مستدعى بواسطة اللّيدر** ⚡\n\n" \
                         f"📊 **الأصل المالي:** {asset}\n" \
                         f"⚙️ **حالة الحركة:** {signal['type']}\n" \
                         f"🟢 **سعر الدخول:** {signal['entry']}\n" \
                         f"🎯 **الهدف (TP):** {sig['tp'] if 'sig' in locals() else signal['tp']}\n" \
                         f"🛑 **وقف الخسارة (SL):** {sig['sl'] if 'sig' in locals() else signal['sl']}\n" \
                         f"⭐ **دقة المطابقة الفنية للسيستم:** {score}/10"
            keyboard = [[
                InlineKeyboardButton("✅ موافقة ونشر بالـ VIP", callback_data=f"vip_pay_{SIGNAL_ID_COUNTER}"),
                InlineKeyboardButton("❌ إلغاء الصفقة", callback_data=f"vip_rej_{SIGNAL_ID_COUNTER}")
            ]]
            await update.message.reply_text(admin_text, reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            await update.message.reply_text(f"❌ تم الفحص فوراً، ولكن لا توجد إشارة فنية مستقرة ومؤكدة لـ {asset} حالياً.")
    except Exception as e:
        await update.message.reply_text(f"❌ حدث خطأ تقني أثناء سحب البيانات الفورية: {e}")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    try:
        if hasattr(database, 'add_user'): database.add_user(user.id, user.username)
    except: pass
    keyboard = [['📊 طلب صفقة مضاربة', '👑 مجاني VIP اشتراك'], ['📞 الدعم الفني']]
    await update.message.reply_text(
        f"أهلاً بك يا {user.first_name} في نظام الرادار الآلي المطوّر 🚀\n\n"
        f"🎁 حسابك مفعل تلقائياً للحصول على **(3 صفقات مجانية يومياً)** فائقة الدقة لتجربة مصداقية السيستم بنفسك قبل الانتقال للـ VIP!", 
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

async def handle_text_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id
    username = update.effective_user.username or "بدون معرف"

    # 1️⃣ معالجة طلب توثيق JustMarkets
    if context.user_data.get('awaiting_jm_id'):
        context.user_data['awaiting_jm_id'] = False
        if not text.isdigit():
            await update.message.reply_text("⚠️ خطأ! أدخل أرقام حسابك المكون من أرقام فقط.")
            return
        try:
            if hasattr(database, 'update_justmarkets_id'): database.update_justmarkets_id(user_id, text)
        except: pass
        await update.message.reply_text("🎉 تم رفع طلبك بنجاح! جاري تدقيقه من قبل الإدارة لتفعيل ميزات الـ VIP غير المحدودة.")
        admin_alert = f"👤 **طلب توثيق عميل جديد**\n\n🔹 المشترك: @{username}\n🔹 الأي دي: {user_id}\n🔑 رقم حساب JustMarkets: {text}\n\nراجع لوحة الشركاء وفعل الحساب إذا كان تحت وكالتك بنجاح."
        await context.bot.send_message(chat_id=ADMIN_GROUP_ID, text=admin_alert)
        return

    # 2️⃣ معالجة استقبال رسائل الدعم الفني وتحويلها للإدارة
    if context.user_data.get('awaiting_support'):
        context.user_data['awaiting_support'] = False
        await update.message.reply_text("✅ تم إرسال رسالتك لفريق الدعم الفني بنجاح، وسيتم الرد عليك في أقرب وقت يا غالي!")
        support_alert = f"📞 **رسالة واردة للدعم الفني**\n\n👤 **من المشترك:** @{username}\n🆔 **الأي دي:** {user_id}\n\n💬 **نص الرسالة:**\n{text}"
        await context.bot.send_message(chat_id=ADMIN_GROUP_ID, text=support_alert)
        return

    # 3️⃣ زر صفقات المضاربة (تم حمايته تماماً من الانهيار)
    if text == '📊 طلب صفقة مضاربة':
        is_vip = False
        try:
            user_data = None
            if hasattr(database, 'get_user'): user_data = database.get_user(user_id)
            if user_data and isinstance(user_data, dict):
                is_vip = bool(user_data.get('justmarkets_id'))
        except Exception as e:
            print(f"🛡️ جدار حماية الداتابيز تجاوز الفحص بأمان: {e}")

        if not is_vip:
            current_count = FREE_TRIAL_COUNTER.get(user_id, 0)
            if current_count >= 3:
                await update.message.reply_text(
                    "❌ **انتهت الفترة التجريبية المجانية الخاصة بك اليوم!**\n\n"
                    "لأن صفقاتنا قيمتها عالية ومصفاة بدقة، نمنح 3 إشارات فقط للزوار الجدد.\n"
                    "لتفتح الصفقات مدى الحياة وبشكل غير محدود مجاناً، قم بفتح حساب عبر رابط وكالتنا الحين وضعه هنا 👇",
                    reply_markup=ReplyKeyboardMarkup([['👑 مجاني VIP اشتراك']], resize_keyboard=True)
                )
                return
            FREE_TRIAL_COUNTER[user_id] = current_count + 1
            await update.message.reply_text(f"🎁 إشارة تجريبية: أنت تستهلك الآن الصفقة رقم ({FREE_TRIAL_COUNTER[user_id]} من 3) المتاحة لك مجاناً اليوم.")

        keyboard = [
            [InlineKeyboardButton("🏆 ذهب (XAU/USD)", callback_data='asset_XAUUSD')],
            [InlineKeyboardButton("EUR/USD (فوركس)", callback_data='asset_EURUSD'), InlineKeyboardButton("BTC/USDT (كريبتو)", callback_data='asset_BTCUSDT')]
        ]
        await update.message.reply_text("📊 إختر الأصل المالي المطلوب استخراج إشارته الحية الحين وبكل دقة:", reply_markup=InlineKeyboardMarkup(keyboard))
        
    elif text == '👑 مجاني VIP اشتراك':
        keyboard = [
            [InlineKeyboardButton("🔗 1. فتح حساب في JustMarkets وبدء التداول", url=config.JUSTMARKETS_REF_LINK)],
            [InlineKeyboardButton("📝 2. ربط وتوثيق رقم حسابك بالبوت", callback_data='register')]
        ]
        await update.message.reply_text("👇 للحصول على الخدمات والتحليلات داخل جروب الـ VIP بشكل دائم وغير محدود، اتبع الخطوات التالية:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif text == '📞 الدعم الفني':
        context.user_data['awaiting_support'] = True
        await update.message.reply_text("📩 أرسل رسالتك الحين وسيتم تحويلها مباشرة لجروب الإدارة لمتابعتك فوراً.")

async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == 'register':
        context.user_data['awaiting_jm_id'] = True
        await query.message.reply_text("📝 أرسل الحين رقم حسابك (ID) المفتوح في JustMarkets المكون من أرقام فقط:")
        return

    if data.startswith("vip_pay_"):
        sig_id = int(data.split("_")[2])
        sig = PENDING_SIGNALS.get(sig_id)
        if sig:
            vip_text = f"🚨 **إشارة تداول رسمية معتمدة من الإدارة** 👑\n\n" \
                       f"📊 **الأصل المالي:** {sig['asset']}\n" \
                       f"⚙️ **نوع الأمر:** {sig['type']}\n" \
                       f" ---------------------------------- \n" \
                       f"🟢 **سعر الدخول المعتمد:** {sig['entry']}\n" \
                       f"🎯 **هدف جني الأرباح (TP):** {sig['tp']}\n" \
                       f"🛑 **وقف الخسارة (SL):** {sig['sl']}\n\n" \
                       f"⚠️ جروب الـ VIP الرسمي - تداولوا بحذر وإدارة رأس مال حكيمة! 🔥"
            try:
                await context.bot.send_message(chat_id=VIP_GROUP_ID, text=vip_text)
                await query.edit_message_text(f"✅ تم اعتماد الصفقة بنجاح ونشرها فوراً داخل جروب الـ VIP!")
                PENDING_SIGNALS.pop(sig_id, None)
            except Exception as e:
                await query.edit_message_text(f"❌ تم الاعتماد ولكن فشل النشر الآلي. الخطأ: {e}")
        else:
            await query.edit_message_text("⚠️ هذه الصفقة تم معالجتها سابقاً أو انتهت صلاحيتها الفنية.")
        return

    if data.startswith("vip_rej_"):
        sig_id = int(data.split("_")[2])
        PENDING_SIGNALS.pop(sig_id, None)
        await query.edit_message_text("❌ تم رفض هذه الإشارة واستبعادها بنجاح بواسطة اللّيدر.")
        return

    if data.startswith("asset_"):
        asset = data.split("_")[1]
        keyboard = [
            [InlineKeyboardButton("⏱️ 15 دقيقة (15m)", callback_data=f"tf_{asset}_15m"), InlineKeyboardButton("⏱️ 30 دقيقة (30m)", callback_data=f"tf_{asset}_30m")],
            [InlineKeyboardButton("⏱️ ساعة (1h)", callback_data=f"tf_{asset}_1h"), InlineKeyboardButton("⏱️ 4 ساعات (4h)", callback_data=f"tf_{asset}_4h")]
        ]
        await query.edit_message_text(f"⏱️ إختر الفريم الزمني المطلوب لتحليل {asset}:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("tf_"):
        parts = data.split("_")
        asset, timeframe = parts[1], parts[2]
        await query.edit_message_text(f"🔍 الرادار الذكي يفحص ويحلل {asset} على فريم ({timeframe}) بأعلى معايير الدقة والصفاء الفني... ثواني ⏳")
        
        try:
            df = analyzer.get_live_data(asset, timeframe)
            signal, score = analyzer.calculate_signals(df)
            
            if signal:
                reply_text = f"🎯 **نتائج رادار التحليل الفني المصفّى** 🎯\n\n" \
                             f"🔹 **الأصل:** {asset} | **الفريم:** {timeframe}\n" \
                             f" ---------------------------------- \n" \
                             f"📈 **الحالة الفنية للترند:** {signal['type']}\n" \
                             f"🟢 **نقطة الدخول المقترحة:** {signal['entry']}\n" \
                             f"🎯 **الهدف المحسوب (TP):** {signal['tp']}\n" \
                             f"🛑 **وقف الخسارة (SL):** {signal['sl']}\n" \
                             f"⭐ **قوة تأكيد الاستراتيجية الحالية:** {score}/10"
            else:
                reply_text = f"❌ الرادار يفحص الأسواق الآن بدقة، ولكن لا توجد إشارة نقية 100% متطابقة لـ {asset} على فريم {timeframe} حالياً. انتظر فرصة أفضل لحماية حسابك."
            await query.message.reply_text(reply_text)
        except Exception as e:
            await query.message.reply_text(f"❌ عذراً، حدثت مشكلة تقنية مؤقتة أثناء جلب الشموع الحية: {e}")

if __name__ == '__main__':
    TOKEN = "8518436165:AAH2-DjOv0lh9EPpeatvKhAIX-l0DvvvIfY"
    application = Application.builder().token(TOKEN).post_init(post_init).build()
    
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("check", check_command)) 
    application.add_handler(CallbackQueryHandler(handle_callback_query))
    from telegram.ext import filters
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_messages))
    
    print("Multi-Group Protected System is fully online. Ready.")
    application.run_polling()
