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
    return "Official High-Precision Multi-Group System with Webhooks is Active!"

@app.route('/webhook', methods=['POST'])
def tradingview_webhook():
    global application_global
    data = request.json
    if not data or not application_global:
        return jsonify({"status": "ignored", "reason": "no data or bot not ready"}), 400
        
    asset = data.get('asset', 'XAUUSD').upper()
    signal_type = data.get('type', 'BUY LIMIT ⏳')
    entry = data.get('entry', '0.0')
    tp = data.get('tp', '0.0')
    sl = data.get('sl', '0.0')
    
    vip_text = f"🚨 *إشارة عاجلة مدعومة برادار الحيتان (TradingView)* 👑\n\n" \
               f"📊 *الأصل المالي:* `{asset}`\n" \
               f"⚙️ *نوع الأمر المكتشف:* {signal_type}\n" \
               f" ---------------------------------- \n" \
               f"🟢 *سعر الدخول المؤسسي:* `{entry}`\n" \
               f"🎯 *الهدف الخاطف (TP):* `{tp}`\n" \
               f"🛑 *وقف الخسارة الآمن (SL):* `{sl}`\n\n" \
               f"⚠️ *تم رصد منطقة الارتداد مسبقاً عبر نظام الـ Webhooks اللحظي!* 🔥"
               
    asyncio.run_coroutine_threadsafe(
        application_global.bot.send_message(chat_id=-1004372200363, text=vip_text, parse_mode="Markdown"),
        application_global.loop
    )
    return jsonify({"status": "success", "msg": "Signal injected to Telegram VIP Group!"}), 200

def run(): 
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
Thread(target=run, daemon=True).start()

import config
import database
import analyzer

ADMIN_GROUP_ID = -1003310992331
VIP_GROUP_ID = -1004372200363

PENDING_SIGNALS = {}
SIGNAL_ID_COUNTER = 0
FREE_TRIAL_COUNTER = {}
GOLDEN_SIGNAL_TRACKER = {}  
LAST_SENT_SIGNALS = {}  

async def auto_signal_scheduler(application: Application):
    global SIGNAL_ID_COUNTER
    print("... تم إطلاق رادار الفحص التلقائي الذكي للإدارة (مانع التكرار نشط) ...")
    await asyncio.sleep(10)
    while True:
        try:
            for asset in ["XAUUSD", "EURUSD", "BTCUSDT"]:
                df = analyzer.get_live_data(asset, "30m")
                signal, score = analyzer.calculate_signals(df, asset)
                
                if signal and score >= 8:
                    signal_fingerprint = f"{signal['type']}_{signal['entry']}"
                    if LAST_SENT_SIGNALS.get(asset) == signal_fingerprint:
                        continue
                        
                    LAST_SENT_SIGNALS[asset] = signal_fingerprint
                    SIGNAL_ID_COUNTER += 1
                    PENDING_SIGNALS[SIGNAL_ID_COUNTER] = {
                        "asset": asset, "type": signal['type'], "entry": signal['entry'], "tp": signal['tp'], "sl": signal['sl']
                    }
                    
                    admin_text = f"💎 *رادار الإدارة المباشر (فرصة جديدة فريدة)* 💎\n\n" \
                                 f"📊 *الأصل المالي:* `{asset}`\n" \
                                 f"⚙️ *نوع الإشارة:* {signal['type']}\n" \
                                 f" ---------------------------------- \n" \
                                 f"🟢 *سعر الدخول المقترح:* `{signal['entry']}`\n" \
                                 f"🎯 *الهدف (TP):* `{signal['tp']}`\n" \
                                 f"🛑 *وقف الخسارة (SL):* `{signal['sl']}`\n" \
                                 f"⭐ *قوة دقة الفلتر الفني:* {score}/10\n\n" \
                                 f"👇 اضغط على قرارك لحقن الصفقة رسمياً في جروب الـ VIP:"
                                 
                    keyboard = [[
                        InlineKeyboardButton("✅ موافقة ونشر بالـ VIP", callback_data=f"vip_pay_{SIGNAL_ID_COUNTER}"),
                        InlineKeyboardButton("❌ إلغاء واستبعاد", callback_data=f"vip_rej_{SIGNAL_ID_COUNTER}")
                    ]]
                    await application.bot.send_message(chat_id=ADMIN_GROUP_ID, text=admin_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        except Exception as e:
            print(f"خطأ في مجدول الإدارة: {e}")
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
        await update.message.reply_text("⚠️ يرجى كتابة اسم الأصل المالي مع الأمر، مثال:\n`/check XAUUSD`")
        return
    asset = context.args[0].upper()
    await update.message.reply_text(f"🚀 أمر فوري من اللّيدر! جاري فحص {asset} الحين بقوة الفلاتر المؤسسية ومواقع التحليل...")
    
    try:
        df = analyzer.get_live_data(asset, "30m")
        signal, score = analyzer.calculate_signals(df, asset)
        if signal:
            SIGNAL_ID_COUNTER += 1
            PENDING_SIGNALS[SIGNAL_ID_COUNTER] = {
                "asset": asset, "type": signal['type'], "entry": signal['entry'], "tp": signal['tp'], "sl": signal['sl']
            }
            admin_text = f"⚡ *تحليل فوري مستدعى بواسطة اللّيدر* ⚡\n\n" \
                         f"📊 *الأصل المالي:* `{asset}`\n" \
                         f"⚙️ *حالة الحركة:* {signal['type']}\n" \
                         f"🟢 *سعر الدخول:* `{signal['entry']}`\n" \
                         f"🎯 *الهدف (TP):* `{signal['tp']}`\n" \
                         f"🛑 *وقف الخسارة (SL):* `{signal['sl']}`\n" \
                         f"⭐ *دقة المطابقة الفنية والتحليلية:* {score}/10"
            keyboard = [[
                InlineKeyboardButton("✅ موافقة ونشر بالـ VIP", callback_data=f"vip_pay_{SIGNAL_ID_COUNTER}"),
                InlineKeyboardButton("❌ إلغاء الصفقة", callback_data=f"vip_rej_{SIGNAL_ID_COUNTER}")
            ]]
            await update.message.reply_text(admin_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        else:
            await update.message.reply_text(f"❌ تم الفحص فوراً، ولكن لا توجد إشارة فنية مستقرة ومؤكدة لـ {asset} حالياً (أو خارج ساعات السيولة الرسمية للذهب).")
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
        f"🎁 حسابك مفعل تلقائياً للحصول على **(3 صفقات ناجحة يومياً)** فائدة الدقة لتجربة مصداقية السيستم بنفسك قبل الانتقال للـ VIP!", 
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

async def handle_text_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id
    username = update.effective_user.username or "بدون معرف"

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

    if context.user_data.get('awaiting_support'):
        context.user_data['awaiting_support'] = False
        await update.message.reply_text("✅ تم إرسال رسالتك لفريق الدعم الفني بنجاح، وسيتم الرد عليك في أقرب وقت يا غالي!")
        support_alert = f"📞 **رسالة واردة للدعم الفني**\n\n👤 **من المشترك:** @{username}\n🆔 **الأي دي:** {user_id}\n\n💬 **نص الرسالة:**\n{text}"
        await context.bot.send_message(chat_id=ADMIN_GROUP_ID, text=support_alert)
        return

    if text == '📊 طلب صفقة مضاربة':
        is_vip = False
        try:
            user_data = None
            if hasattr(database, 'get_user'): user_data = database.get_user(user_id)
            if user_data and isinstance(user_data, dict):
                is_vip = bool(user_data.get('justmarkets_id'))
        except: pass

        if not is_vip:
            current_count = FREE_TRIAL_COUNTER.get(user_id, 0)
            if current_count >= 3:
                await update.message.reply_text(
                    "❌ **انتهت الفترة التجريبية المجانية الخاصة بك اليوم!**\n\n"
                    "لأن صفقاتنا قيمتها عالية ومصفاة بدقة، نمنح 3 إشارات ناجحة فقط للزوار الجدد.\n"
                    "لتفتح الصفقات مدى الحياة وبشكل غير محدود مجاناً، قم بفتح حساب عبر رابط وكالتنا الحين وضعه هنا 👇",
                    reply_markup=ReplyKeyboardMarkup([['👑 مجاني VIP اشتراك']], resize_keyboard=True)
                )
                return

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
    user_id = update.effective_user.id

    if data == 'register':
        context.user_data['awaiting_jm_id'] = True
        await query.message.reply_text("📝 أرسل الحين رقم حسابك (ID) المفتوح في JustMarkets المكون من أرقام فقط:")
        return

    if data.startswith("vip_pay_"):
        sig_id = int(data.split("_")[2])
        sig = PENDING_SIGNALS.get(sig_id)
        if sig:
            vip_text = f"🚨 *إشارة تداول رسمية معتمدة من الإدارة* 👑\n\n" \
                       f"📊 *الأصل المالي:* `{sig['asset']}`\n" \
                       f"⚙️ *نوع الأمر:* {sig['type']}\n" \
                       f" ---------------------------------- \n" \
                       f"🟢 *سعر الدخول المعتمد:* `{sig['entry']}`\n" \
                       f"🎯 *هدف جني الأرباح (TP):* `{sig['tp']}`\n" \
                       f"🛑 *وقف الخسارة (SL):* `{sig['sl']}`\n\n" \
                       f"⚠️ جروب الـ VIP الرسمي - تداولوا بحذر وإدارة رأس مال حكيمة! 🔥"
            try:
                await context.bot.send_message(chat_id=VIP_GROUP_ID, text=vip_text, parse_mode="Markdown")
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
        
        is_vip = False
        try:
            user_data = None
            if hasattr(database, 'get_user'): user_data = database.get_user(user_id)
            if user_data and isinstance(user_data, dict):
                is_vip = bool(user_data.get('justmarkets_id'))
        except: pass

        if not is_vip and FREE_TRIAL_COUNTER.get(user_id, 0) >= 3:
            await query.edit_message_text("❌ انتهى رصيد صفقاتك المجانية المتاحة لليوم! يرجى الترقية للـ VIP للاستمرار.")
            return

        await query.edit_message_text(f"🔍 الرادار الذكي يفحص ويحلل {asset} على فريم ({timeframe})... ثواني ⏳")
        
        try:
            df = analyzer.get_live_data(asset, timeframe)
            signal, score = analyzer.calculate_signals(df, asset)
            
            if signal:
                if not is_vip:
                    if score >= 9 and GOLDEN_SIGNAL_TRACKER.get(user_id, 0) == 0:
                        GOLDEN_SIGNAL_TRACKER[user_id] = 1 
                        remaining = 3 - FREE_TRIAL_COUNTER.get(user_id, 0)
                        trial_footer = f"\n\n🎁 *[هدية ألماسيّة من اللّيدر]:* هذه الصفقة قوتها الفنية خارقة ({score}/10)، ولأنها فرصة نادرة تم إعطاؤها للجميع *مجاناً بالكامل دون خصم من رصيدك اليومي!* متبقي لك: ({remaining} من 3)."
                    else:
                        FREE_TRIAL_COUNTER[user_id] = FREE_TRIAL_COUNTER.get(user_id, 0) + 1
                        remaining = 3 - FREE_TRIAL_COUNTER[user_id]
                        if score >= 9:
                            trial_footer = f"\n\n🎁 *[ملاحظة الرصيد]:* هذه الصفقة قوتها ({score}/10) ولكن نظراً للاستفادة السابقة من الهدية اليوم، تم احتسابها من رصيدك. متبقي لك: ({remaining} من 3)."
                        else:
                            trial_footer = f"\n\n🎁 *[ملاحظة الرصيد]:* تم احتساب صفقة حقيقية ناجحة. متبقي لك اليوم: ({remaining} من 3) صفقات مجانية."
                else:
                    trial_footer = ""

                reply_text = f"🎯 *نتائج رادار التحليل الفني المصفّى (على الفرازة)* 🎯\n\n" \
                             f"🔹 *الأصل:* `{asset}` | *الفريم:* {timeframe}\n" \
                             f" ---------------------------------- \n" \
                             f"📈 *الحالة الفنية للترند:* {signal['type']}\n" \
                             f"🟢 *نقطة الدخول المقترحة:* `{signal['entry']}`\n" \
                             f"🎯 *الهدف المحسوب (TP):* `{signal['tp']}`\n" \
                             f"🛑 *وقف الخسارة (SL):* `{signal['sl']}`\n" \
                             f"⭐ *قوة تأكيد الاستراتيجية الحالية:* {score}/10" + trial_footer
            else:
                reply_text = f"❌ الرادار يفحص الأسواق الآن بدقة، ولكن لا توجد إشارة نقية 100% متطابقة لـ {asset} على فريم {timeframe} حالياً (أو خارج ساعات السيولة الرسمية للذهب).\n\n🛡️ *حفاظاً على أمان حسابك لم يتم توليد توصية ولم يتم خصم أي شيء من رصيدك اليومي المجاني.*"
                
            await query.message.reply_text(reply_text, parse_mode="Markdown")
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
