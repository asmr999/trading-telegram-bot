from flask import Flask, request, jsonify
from threading import Thread
import os
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, CallbackQueryHandler

app = Flask('')
application_global = None  

@app.route('/')
def home(): 
    return "Official High-Precision Multi-Group AI System is Active!"

@app.route('/webhook', methods=['POST'])
def tradingview_webhook():
    global application_global
    data = request.json
    if not data or not application_global: return jsonify({"status": "ignored"}), 400
        
    asset = data.get('asset', 'XAUUSD').upper()
    signal_type = data.get('type', 'BUY LIMIT ⏳')
    entry = data.get('entry', '0.0')
    tp = data.get('tp', '0.0')
    sl = data.get('sl', '0.0')
    
    vip_text = f"🚨 إشارة عاجلة مدعومة برادار الحيتان (TradingView) 👑\n\n" \
               f"📊 الأصل المالي: {asset}\n" \
               f"⚙️ نوع الأمر المكتشف: {signal_type}\n" \
               f" ---------------------------------- \n" \
               f"🟢 سعر الدخول المؤسسي: `{entry}`\n" \
               f"🎯 الهدف الخاطف (TP): `{tp}`\n" \
               f"🛑 وقف الخسارة الآمن (SL): `{sl}`\n\n" \
               f"🔗 كود وكالتنا المعتمد للحسابات القديمة: tr42sl0svg"
               
    keyboard = [[InlineKeyboardButton("⚡ تداول الآن عبر JustMarkets", url="https://justmarkets.com/?ref=tr42sl0svg")]]
    asyncio.run_coroutine_threadsafe(
        application_global.bot.send_message(chat_id=-1004372200363, text=vip_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown"),
        application_global.loop
    )
    return jsonify({"status": "success"}), 200

def run(): 
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
Thread(target=run, daemon=True).start()

import config
import database
import analyzer
import ai_analyst

ADMIN_GROUP_ID = -1003310992331
VIP_GROUP_ID = -1004372200363

PENDING_SIGNALS = {}
SIGNAL_ID_COUNTER = 0
FREE_TRIAL_COUNTER = {}
LAST_SENT_SIGNALS = {}  

async def auto_signal_scheduler(application: Application):
    global SIGNAL_ID_COUNTER
    print("... تم إطلاق رادار الفحص التلقائي وجدار الـ AI الذكي (نشط) ...")
    await asyncio.sleep(10)
    while True:
        try:
            for asset in ["XAUUSD", "EURUSD", "BTCUSDT"]:
                df = analyzer.get_live_data(asset, "30m")
                signal, score, summary = analyzer.calculate_signals(df, asset)
                
                if signal and score >= 8:
                    signal_fingerprint = f"{signal['type']}_{signal['entry']}"
                    if LAST_SENT_SIGNALS.get(asset) == signal_fingerprint: continue
                    LAST_SENT_SIGNALS[asset] = signal_fingerprint
                    
                    ai_msg = ai_analyst.ask_gemini_analyst(asset, signal['type'], signal['entry'], signal['tp1'], signal['tp2'], signal['sl'], signal['rr'], summary)
                    
                    SIGNAL_ID_COUNTER += 1
                    PENDING_SIGNALS[SIGNAL_ID_COUNTER] = {
                        "asset": asset, "type": signal['type'], "entry": signal['entry'], "tp1": signal['tp1'], "tp2": signal['tp2'], "sl": signal['sl'], "rr": signal['rr'], "ai_msg": ai_msg
                    }
                    
                    admin_text = f"💎 رادار الإدارة المباشر (تأكيد الذكاء الاصطناعي) 💎\n\n" \
                                 f"📊 الأصل المالي: {asset}\n" \
                                 f"⚙️ نوع الإشارة: {signal['type']}\n" \
                                 f"🟢 سعر الدخول: `{signal['entry']}`\n" \
                                 f"🎯 الهدف الأول: `{signal['tp1']}` | الهدف الثاني: `{signal['tp2']}`\n" \
                                 f"🛑 وقف الخسارة: `{signal['sl']}`\n" \
                                 f"⚖️ نسبة العائد/المخاطرة: {signal['rr']}\n" \
                                 f"⭐ قوة الفلتر الرقمي: {score}/10\n\n" \
                                 f"🧠 رؤية وحكم حارس الـ AI (جيمناي):\n{ai_msg}\n\n" \
                                 f"👇 اضغط على قرارك لحقن الصفقة في الـ VIP الحين:"
                                 
                    keyboard = [[
                        InlineKeyboardButton("✅ موافقة ونشر بالـ VIP", callback_data=f"vip_pay_{SIGNAL_ID_COUNTER}"),
                        InlineKeyboardButton("❌ إلغاء واستبعاد", callback_data=f"vip_rej_{SIGNAL_ID_COUNTER}")
                    ]]
                    await application.bot.send_message(chat_id=ADMIN_GROUP_ID, text=admin_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        except Exception as e:
            print(f"خطأ في المجدول: {e}")
        await asyncio.sleep(300)

async def post_init(application: Application):
    global application_global
    application_global = application 
    asyncio.create_task(auto_signal_scheduler(application))

async def check_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global SIGNAL_ID_COUNTER
    chat_id = update.effective_chat.id
    if chat_id != ADMIN_GROUP_ID: return 
    if not context.args:
        await update.message.reply_text("⚠️ يرجى كتابة اسم الأصل المالي، مثال:\n`/check XAUUSD`")
        return
    asset = context.args[0].upper()
    await update.message.reply_text(f"🚀 أمر عاجل من اللّيدر! جاري فحص {asset} بـ 13 مؤشر رقمي وحارس الـ AI الحين...")
    
    try:
        df = analyzer.get_live_data(asset, "30m")
        signal, score, summary = analyzer.calculate_signals(df, asset)
        if signal:
            ai_msg = ai_analyst.ask_gemini_analyst(asset, signal['type'], signal['entry'], signal['tp1'], signal['tp2'], signal['sl'], signal['rr'], summary)
            SIGNAL_ID_COUNTER += 1
            PENDING_SIGNALS[SIGNAL_ID_COUNTER] = {
                "asset": asset, "type": signal['type'], "entry": signal['entry'], "tp1": signal['tp1'], "tp2": signal['tp2'], "sl": signal['sl'], "rr": signal['rr'], "ai_msg": ai_msg
            }
            admin_text = f"⚡ تحليل فوري مستدعى بواسطة اللّيدر ⚡\n\n" \
                         f"📊 الأصل المالي: {asset}\n" \
                         f"⚙️ حالة الحركة: {signal['type']}\n" \
                         f"🟢 سعر الدخول المكتشف: `{signal['entry']}`\n" \
                         f"🎯 الأهداف: TP1=`{signal['tp1']}` | TP2=`{signal['tp2']}`\n" \
                         f"🛑 وقف الخسارة (SL): `{signal['sl']}`\n" \
                         f"⚖️ النسبة الحسابية (RR): {signal['rr']}\n" \
                         f"⭐ دقة مطابقة الفلاتر: {score}/10\n\n" \
                         f"🧠 رؤية وتفسير حارس الـ AI (جيمناي):\n{ai_msg}"
            keyboard = [[
                InlineKeyboardButton("✅ موافقة ونشر بالـ VIP", callback_data=f"vip_pay_{SIGNAL_ID_COUNTER}"),
                InlineKeyboardButton("❌ إلغاء الصفقة", callback_data=f"vip_rej_{SIGNAL_ID_COUNTER}")
            ]]
            await update.message.reply_text(admin_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        else:
            await update.message.reply_text(f"❌ تم الفحص، ولكن لا توجد إشارة مستقرة وقوية لـ {asset} حالياً (أو خارج ساعات السيولة الرسمية).")
    except Exception as e:
        await update.message.reply_text(f"❌ حدث خطأ تقني في سحب الشموع: {e}")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    keyboard = [['📊 طلب صفقة مضاربة', '👑 مجاني VIP اشتراك'], ['📞 الدعم الفني']]
    await update.message.reply_text(
        f"أهلاً بك يا {user.first_name} في نظام رادار الـ AI المطوّر لشركة الاستثمار الخاصة بنا 🚀\n\n"
        f"🎁 رصيدك مفعل تلقائياً للحصول على (3 صفقات ناجحة يومياً) لتجربة مصداقية وحش الذكاء الاصطناعي بنفسك الحين قبل الانتقال للـ VIP!", 
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

async def handle_text_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id
    username = update.effective_user.username or "بدون معرف"

    if text == '📊 طلب صفقة مضاربة':
        keyboard = [
            [InlineKeyboardButton("🏆 ذهب (XAU/USD)", callback_data='asset_XAUUSD')],
            [InlineKeyboardButton("EUR/USD (فوركس)", callback_data='asset_EURUSD'), InlineKeyboardButton("BTC/USDT (كريبتو)", callback_data='asset_BTCUSDT')]
        ]
        await update.message.reply_text("📊 إختر الأصل المالي المطلوب استخراج إشارته الحية الحين بدقة الفلاتر الـ 13 وجيمناي ومجاناً:", reply_markup=InlineKeyboardMarkup(keyboard))
    elif text == '👑 مجاني VIP اشتراك':
        keyboard = [
            [InlineKeyboardButton("🔗 1. فتح حساب في JustMarkets وبدء التداول", url="https://justmarkets.com/?ref=tr42sl0svg")],
            [InlineKeyboardButton("📝 2. ربط رقم حسابك بالبوت الحين", callback_data='register')]
        ]
        await update.message.reply_text(f"👇 للحصول على الخدمات والتحليلات مجاناً مدى الحياة داخل جروب الـ VIP، اتبع الخطوات التالية:\n\n🔑 كود وكالتنا اليدوي للحسابات القديمة: tr42sl0svg", reply_markup=InlineKeyboardMarkup(keyboard))
    elif text == '📞 الدعم الفني':
        context.user_data['awaiting_support'] = True
        await update.message.reply_text("📩 أرسل رسالتك الحين وسيتم تحويلها لجروب الإدارة لمتابعتك فوراً.")

async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = update.effective_user.id

    if data == 'register':
        context.user_data['awaiting_jm_id'] = True
        await query.message.reply_text("📝 أرسل الحين رقم حسابك (ID) المفتوح تحت وكالتنا المكون من أرقام فقط:")
        return

    if data.startswith("vip_pay_"):
        sig_id = int(data.split("_")[2])
        sig = PENDING_SIGNALS.get(sig_id)
        if sig:
            vip_text = f"🚨 إشارة تداول رسمية معتمدة على الفرازة 👑\n\n" \
                       f"📊 الأصل المالي: {sig['asset']}\n" \
                       f"⚙️ نوع الأمر: {sig['type']}\n" \
                       f" ---------------------------------- \n" \
                       f"🟢 سعر الدخول المعتمد: `{sig['entry']}`\n" \
                       f"🎯 هدف أول خاطف: `{sig['tp1']}`\n" \
                       f"🏆 هدف ثانٍ حوت: `{sig['tp2']}`\n" \
                       f"🛑 وقف الخسارة آمن: `{sig['sl']}`\n" \
                       f"⚖️ النسبة المحسوبة (RR): {sig['rr']}\n\n" \
                       f"🧠 تحليل وتفسير وحش الـ AI (جيمناي):\n{sig['ai_msg']}\n\n" \
                       f"⚠️ تداولوا بحذر وبإدارة صارمة لرأس المال! كود الشريك لربط الحسابات: tr42sl0svg"
                       
            keyboard = [[InlineKeyboardButton("⚡ تداول الآن عبر JustMarkets", url="https://justmarkets.com/?ref=tr42sl0svg")]]
            try:
                await context.bot.send_message(chat_id=VIP_GROUP_ID, text=vip_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
                await query.edit_message_text(f"✅ تم اعتماد صفقة الـ AI بنجاح ونشرها بالأزرار التفاعلية الشفافة بالـ VIP!")
                PENDING_SIGNALS.pop(sig_id, None)
            except Exception as e:
                await query.edit_message_text(f"❌ تم الاعتماد ولكن فشل النشر التلقائي: {e}")
        return

    if data.startswith("vip_rej_"):
        sig_id = int(data.split("_")[2])
        PENDING_SIGNALS.pop(sig_id, None)
        await query.edit_message_text("❌ تم رفض الإشارة واستبعادها بنجاح بواسطة اللّيدر.")
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
        
        await query.edit_message_text(f"🔍 رادار الـ AI يغربل ويقنص {asset} على فريم ({timeframe}) مسبقاً الحين... ثواني ⏳")
        
        try:
            df = analyzer.get_live_data(asset, timeframe)
            signal, score, summary = analyzer.calculate_signals(df, asset)
            
            if signal:
                ai_explanation = ai_analyst.ask_gemini_analyst(asset, signal['type'], signal['entry'], signal['tp1'], signal['tp2'], signal['sl'], signal['rr'], summary)
                reply_text = f"🎯 نتائج رادار الـ AI المصفّى (على الفرازة) 🎯\n\n" \
                             f"🔹 الأصل: {asset} | الفريم: {timeframe}\n" \
                             f" ---------------------------------- \n" \
                             f"📈 الحالة الفنية للترند: {signal['type']}\n" \
                             f"🟢 نقطة الدخول المقترحة: `{signal['entry']}`\n" \
                             f"🎯 هدف أول (خاطف): `{signal['tp1']}`\n" \
                             f"🏆 هدف ثانٍ (حوت): `{signal['tp2']}`\n" \
                             f"🛑 وقف الخسارة آمن: `{signal['sl']}`\n" \
                             f"⚖️ نسبة العائد/المخاطرة: {signal['rr']}\n" \
                             f"⭐ قوة تأكيد الاستراتيجية: {score}/10\n\n" \
                             f"🧠 تحليل وتفسير وحش الـ AI (جيمناي):\n{ai_explanation}\n\n" \
                             f"🔑 كود الشريك المعتمد لربط حسابك: tr42sl0svg"
                             
                keyboard = [[InlineKeyboardButton("⚡ تداول الآن عبر JustMarkets", url="https://justmarkets.com/?ref=tr42sl0svg")]]
                await query.message.reply_text(reply_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
            else:
                reply_text = f"❌ الرادار يفحص الأسواق الآن بدقة الفلاتر الـ 13، ولكن لا توجد إشارة نقية ومطابقة 100% حالياً لـ {asset} على فريم {timeframe} (أو خارج ساعات السيولة الحوتية).\n\n🛡️ حفاظاً على أمان حسابك لم يتم توليد توصية."
                await query.message.reply_text(reply_text, parse_mode="Markdown")
               except Exception as e:
            pass 
            # 📸 دالة استقبال لقطات الشاشة وتحويلها لـ AI الحوت الهجين
async def handle_chart_photo(update, context):
    status_msg = await update.message.reply_text("🦅 أمر عاجل من اللّيدر! جاري فحص الشارت بالعين البصرية لـ AI الحوت... ثواني ملوكية!")
    try:
        photo_file = await update.message.photo[-1].get_file()
        image_bytes = await photo_file.download_as_bytearray()
        
        from ai_analyst import analyze_chart_image
        analysis_text = analyze_chart_image(image_bytes)
        
        await update.message.reply_text(analysis_text)
    except Exception as e:
        await update.message.reply_text(f"❌ عذراً ليدر، حدث خطأ أثناء معالجة الصورة: {str(e)}

    if __name__ == '__main__':
    TOKEN = os.environ.get("BOT_TOKEN", "8518436165:AAH2-DjOv0lh9EPpeatvKhAIX-1ODvvvIfY")
    application = Application.builder().token(TOKEN).post_init(post_init).build()
    
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("check", check_command))
    application.add_handler(CallbackQueryHandler(handle_callback_query))
    
    # 📥 السطر السحري اللي طار منك وأنت بتعدل فوق هيه رجعناه
    from telegram.ext import MessageHandler, filters
    
    application.add_handler(MessageHandler(filters.PHOTO, handle_chart_photo))
    
    print("Multi-Group Deep AI System is fully online. Ready.")
    application.run_polling()
