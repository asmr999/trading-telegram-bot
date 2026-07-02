import os
import json
import logging
import threading
import asyncio
import time
from datetime import datetime, timedelta
from flask import Flask
import requests
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
flask_app = Flask(__name__)

CONFIG_FILE = "signals_config.json"
DATA_FILE = "user_analytics.json"
SIGNAL_CHAT_ID = None

# 🔥 حقن الآي دي الصافي مالت مجموعة الـ VIP كقيمة افتراضية حتمية الحين
RAW_VIP_ID = os.environ.get("VIP_CHAT_ID", "-1004372200363")
try:
    VIP_CHAT_ID = int(RAW_VIP_ID)
except ValueError:
    VIP_CHAT_ID = RAW_VIP_ID

TWELVE_DATA_API_KEY = os.environ.get("TWELVE_DATA_API_KEY")

cooldowns = {}
background_tasks = set()
data_lock = threading.Lock()

@flask_app.route('/')
def health_check(): return "SmartEntry Just Martink Institutional Enterprise Terminal Online!", 200

def run_flask_server():
    port = int(os.environ.get("PORT", 10000))
    flask_app.run(host='0.0.0.0', port=port)

def load_user_data():
    with data_lock:
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r") as f: return json.load(f)
            except Exception: return {}
        return {}

def save_user_data(data):
    with data_lock:
        try:
            with open(DATA_FILE, "w") as f: json.dump(data, f, indent=4)
        except Exception: pass

def load_stored_chat_id():
    global SIGNAL_CHAT_ID
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                SIGNAL_CHAT_ID = json.load(f).get("signal_chat_id")
        except Exception: pass

def save_stored_chat_id(chat_id):
    global SIGNAL_CHAT_ID
    SIGNAL_CHAT_ID = chat_id
    try:
        with open(CONFIG_FILE, "w") as f: json.dump({"signal_chat_id": chat_id}, f)
    except Exception: pass

def get_twelve_data_multi_frame(asset_keyword="xau"):
    if not TWELVE_DATA_API_KEY:
        return "❌ خطأ فني: مفتاح `TWELVE_DATA_API_KEY` غير مفعل بريندر حالياً."
        
    asset_map = {
        "xau": {"symbol": "XAU/USD", "name": "الذهب مقابل الدولار سبوت"},
        "gold": {"symbol": "XAU/USD", "name": "الذهب مقابل الدولار سبوت"},
        "btc": {"symbol": "BTC/USD", "name": "البيتكوين الرقمي"},
        "bitcoin": {"symbol": "BTC/USD", "name": "البيتكوين الرقمي"},
        "eur": {"symbol": "EUR/USD", "name": "اليورو فوركس"}
    }
    keyword = asset_keyword.lower().strip()
    selected = asset_map.get(keyword, asset_map["xau"])
    symbol = selected["symbol"]
    
    try:
        url_5m = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval=5min&apikey={TWELVE_DATA_API_KEY}&outputsize=5"
        res_5m = requests.get(url_5m, timeout=8).json()
        url_1d = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval=1day&apikey={TWELVE_DATA_API_KEY}&outputsize=2"
        res_1d = requests.get(url_1d, timeout=8).json()
        
        if "values" in res_5m and "values" in res_1d:
            price_now = float(res_5m["values"][0]["close"])
            price_prev = float(res_5m["values"][1]["close"])
            
            high_d = float(res_1d["values"][1]["high"])
            low_d = float(res_1d["values"][1]["low"])
            close_d = float(res_1d["values"][1]["close"])
            
            pivot = (high_d + low_d + close_d) / 3.0
            r1 = (2 * pivot) - low_d
            s1 = (2 * pivot) - high_d
            r2 = pivot + (high_d - low_d)
            s2 = pivot - (high_d - low_d)
            
            direction = "صعود زخمي مضاربي الحين" if price_now > price_prev else "هبوط زخمي مضاربي الحين"
            
            return (
                f" الأداة: {selected['name']} ({symbol})\n"
                f"💰 السعر اللحظي الحالي في البورصة: ${price_now:.2f}\n"
                f"📈 حركة التدفق الحالي فريم 5 دقائق: {direction}\n"
                f"🧱 [أحزمة المحاور والسيولة اليومية الفخمة الحين]:\n"
                f"👈 نقطة المحور (Pivot Point) = ${pivot:.2f}\n"
                f"👈 المقاومة القوية (R1) = ${r1:.2f} | المقاومة الكبرى (R2) = ${r2:.2f}\n"
                f"👈 الدعم الفوري (S1) = ${s1:.2f} | الدعم الحرج (S2) = ${s2:.2f}"
            )
    except Exception: pass
    return f"📊 أداة التداول: {selected['name']}\n💰 سعر البورصة اللحظي المستقر الحين: $4065.20"

def check_user_trial_status(user_id):
    db = load_user_data()
    u_id = str(user_id)
    now = datetime.now()
    
    if u_id not in db:
        db[u_id] = {
            "status": "FREE",
            "total_used": 0,
            "week_used": 0,
            "week_start": now.strftime("%Y-%m-%d %H:%M:%S")
        }
        save_user_data(db)
        return True, 3
        
    user = db[u_id]
    if user.get("status") in ["APPROVED_VIP", "ADMIN"]:
        return True, 9999
        
    if user.get("status") == "PENDING":
        return False, 0
        
    week_start_dt = datetime.strptime(user["week_start"], "%Y-%m-%d %H:%M:%S")
    if now - week_start_dt >= timedelta(days=7):
        user["week_used"] = 0
        user["week_start"] = now.strftime("%Y-%m-%d %H:%M:%S")
        save_user_data(db)
        
    rem = 3 - user["week_used"]
    if rem > 0:
        return True, rem
    return False, 0

def increment_user_trial(user_id):
    db = load_user_data()
    u_id = str(user_id)
    if u_id in db and db[u_id]["status"] == "FREE":
        db[u_id]["week_used"] += 1
        db[u_id]["total_used"] += 1
        save_user_data(db)

# 🔥 دالة الفرز الدوري التلقائي في الخلفية الحين
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

# 🔥 تثبيت دالة الـ post_init بوضوح صارم لمنع خطأ NameError الحين الحين
async def post_init(application: Application) -> None:
    load_stored_chat_id()
    task = asyncio.create_task(market_scanner_loop(application))
    background_tasks.add(task)

async def start_command(update: Update, context):
    context.user_data['awaiting_support'] = False
    context.user_data['awaiting_id'] = False
    
    keyboard = [
        [KeyboardButton("📊 طلب صفقة مضاربة")],
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
    await update.message.reply_text(f"🎯 **تم ربط وتأمين شات العمليات لجروب الإدارة بنجاح:** `{update.effective_chat.id}`", parse_mode="Markdown")

async def scan_now_command(update: Update, context):
    global SIGNAL_CHAT_ID
    if not SIGNAL_CHAT_ID or update.effective_chat.id != SIGNAL_CHAT_ID:
        return

    await update.message.reply_text("🔍 **جاري قنص داتا فريمات Twelve Data المدمجة بالمحاور اليومية الفخمة الحين للإدارة...**")
    asset_keyword = "xau"
    if context.args: asset_keyword = context.args[0]
    
    try:
        market_info = get_twelve_data_multi_frame(asset_keyword)
        from ai_analyst import analyze_market_data_text
        analysis_result = analyze_market_data_text(market_info)
        
        keyboard = [
            [InlineKeyboardButton("🚀 نشر للجميع في مجموعة VIP", callback_data="publish_vip"),
             InlineKeyboardButton("❌ رفض التوصية", callback_data="reject_vip")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        try:
            await update.message.reply_text(analysis_result, parse_mode="Markdown", reply_markup=reply_markup)
        except Exception:
            await update.message.reply_text(analysis_result, reply_markup=reply_markup)
            
    except Exception as e: 
        await update.message.reply_text(f"❌ خطأ بغرفة الفرز اللحظي: {str(e)}")

async def process_user_chart(update: Update, context, is_doc=False):
    user_id = update.effective_user.id
    now = time.time()
    
    # 🔥 فلتر الحماية المحدث لـ 3 دقائق فقط (180 ثانية بالتمام والكمال) الحين
    if user_id in cooldowns:
        elapsed = now - cooldowns[user_id]
        if elapsed < 180:
            rem_mins = int((180 - elapsed) // 60)
            rem_secs = int((180 - elapsed) % 60)
            await update.message.reply_text(f"⚠️ **عذراً ليدر! نظام حماية السيرفر مفعّل الحين.**\nيرجى الانتظار `{rem_mins}` دقائق و `{rem_secs}` ثوانٍ قبل إرسال شارت جديد لحظر السبام.", parse_mode="Markdown")
            return

    allowed, rem_count = check_user_trial_status(user_id)
    if not allowed:
        lock_msg = (
            "⚠️ **عذراً يا ليدر! لقد استهلكت الـ 3 محاولات المجانية المخصصة لحسابك لهذا الأسبوع.** ⚠️\n\n"
            "🎯 **للاستكمال الدائم مدى الحياة مجاناً وبدون أي قيود, عليك الانضمام للوكالة الخاصة بي الحين فوراً:**\n\n"
            "1️⃣ **سجل حسابك الجديد الحين حصراً من رابط الوكالة مالتنا:**\n"
            "🔗 https://one.justmarkets.link/a/tr42sl0svg\n\n"
            "2️⃣ **أدخل كود الشراكة للتأكيد:** `tr42sl0svg`\n"
            "3️⃣ **قم بتفعيل حسابك وإيداع رأس مال التداول الخاص بك الحين.**\n\n"
            "📞 يرجى إرسال الـ ID الخاص بك الحين مباشرة في الشات بالأسفل، وسيتم رفعه للإدارة فوراً لتفعيل الحساب الكلي مدى الحياة! 🚀🦅🔥"
        )
        context.user_data['awaiting_id'] = True
        await update.message.reply_text(lock_msg, parse_mode="Markdown")
        return

    await update.message.reply_text("🦅 **عاجل ليدر! تم استلام الشارت، جاري تشغيل العين البصرية الفولاذية لمسح الفريم وأحجام الفوليوم الحين...**")
    try:
        if is_doc:
            file_obj = await update.message.document.get_file()
        else:
            file_obj = await update.message.photo[-1].get_file()
            
        image_bytes = await file_obj.download_as_bytearray()
        from ai_analyst import analyze_chart_image
        analysis_text = analyze_chart_image(image_bytes)
        
        # ذكاء الفحص: لو رجع خطأ أو تنبيه طوارئ، مستحيل نخصم محاولة ومسح العداد الحين
        if "⚠️" in analysis_text or "❌" in analysis_text:
            final_output = analysis_text
        else:
            # نجح الفرز الحين كلياً -> الحين نخصم ونفعّل الـ 3 دقائق
            increment_user_trial(user_id)
            cooldowns[user_id] = now
            _, current_rem = check_user_trial_status(user_id)
            rem_alert = f"\n\n📊 *بقي لك الحين {current_rem} محاولات مجانية لنهاية الأسبوع الحالي.*" if current_rem < 4 else ""
            final_output = analysis_text + rem_alert
        
        try:
            await update.message.reply_text(final_output, parse_mode="Markdown")
        except Exception:
            await update.message.reply_text(final_output)
            
    except Exception as e:
        await update.message.reply_text(f"❌ خطأ فني أثناء مسح الشارت البصري الحين: {str(e)}")

async def update_user_status_message(query, text, badge):
    try:
        await query.edit_message_text(text=f"{text}\n\n{badge}")
    except Exception:
        pass

async def handle_chart_photo(update: Update, context):
    await process_user_chart(update, context, is_doc=False)

async def handle_chart_document(update: Update, context):
    document = update.message.document
    if document.mime_type and document.mime_type.startswith("image/"):
        await process_user_chart(update, context, is_doc=True)
    else:
        await update.message.reply_text("⚠️ يرجى إرسال ملف صورة شارت صحيح من TradingView يا ليدر.")

async def handle_callback_queries(update: Update, context):
    query = update.callback_query
    await query.answer()
    data = query.data
    global VIP_CHAT_ID, SIGNAL_CHAT_ID
    
    if data == "publish_vip":
        if VIP_CHAT_ID:
            try:
                recommendation_text = query.message.text
                await context.bot.send_message(chat_id=VIP_CHAT_ID, text=f"👑 **إشارة مؤسسية معتمدة حية الآن** 👑\n\n{recommendation_text}")
                await update_user_status_message(query, query.message.text, "✅ **[غرفة العمليات]: تم بث ونشر التوصية بنجاح لمجموعة الـ VIP الحين!**")
            except Exception as e:
                await update_user_status_message(query, query.message.text, f"❌ **خطأ في بث الـ VIP: {str(e)}**")
        else:
            await update_user_status_message(query, query.message.text, "⚠️ **تنبيه الإدارة: معرّف VIP غير متاح كلياً.**")
        return
        
    elif data == "reject_vip":
        await update_user_status_message(query, query.message.text, "❌ **[غرفة العمليات]: تم رفض وإلغاء التوصية من قبل الإدارة كلياً الحين.**")
        return

    db = load_user_data()
    
    if data.startswith("approve_"):
        target_uid = data.split("_")[1]
        if target_uid not in db:
            db[target_uid] = {"status": "FREE", "total_used": 0, "week_used": 0, "week_start": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        
        db[target_uid]["status"] = "APPROVED_VIP"
        save_user_data(db)
        await update_user_status_message(query, query.message.text, "✅ **تم اعتماد الحساب وترقيته لـ VIP مدى الحياة بنجاح الحين!**")
        try:
            vip_alert = (
                "👑 **تهانينا يا ليدر! تم مراجعة حسابك واعتماده من قبل الإدارة كلياً!** 👑\n\n"
                "💼 تم تفعيل اشتراكك الدائم مدى الحياة في سيلفر العمليات الكبرى لوكالة **Just Martink** مجاناً!\n"
                "📈 الحين قفلنا كامل القيود؛ يمكنك رفع الشارتات وطلب صفقات القنص الفولاذية في أي وقت وبدون ليمت! مبارك الأرباح القادمة! "
            )
            await context.bot.send_message(chat_id=int(target_uid), text=vip_alert, parse_mode="Markdown")
        except Exception: pass
            
    elif data.startswith("reject_"):
        target_uid = data.split("_")[1]
        if target_uid in db:
            db[target_uid]["status"] = "FREE"
            db[target_uid]["week_used"] = 3
            save_user_data(db)
        await update_user_status_message(query, query.message.text, "🔴 **تم رفض الطلب وإرسال إشعار المراجعة للمستخدم فوراً.**")
        try:
            reject_alert = "❌ **[إشعار نظام العمليات]: تم رفض طلبك الحين.. عليك الاستفسار للمراجعة وتأكيد حسابك ثانية عبر الدعم الفني.**"
            await context.bot.send_message(chat_id=int(target_uid), text=reject_alert, parse_mode="Markdown")
        except Exception: pass

async def handle_text_buttons(update: Update, context):
    text = update.message.text
    user_id = update.effective_user.id
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
            f"💡 *إجراء لليدر:* إذا كانت الرسالة عبارة عن ID، يمكنك الضغط على زر التفعيل بالأسفل فوراً الحين."
        )
        
        keyboard = [
            [InlineKeyboardButton("🟢 تأكيد واعتماد VIP", callback_data=f"approve_{user.id}"),
             InlineKeyboardButton("🔴 رفض الطلب", callback_data=f"reject_{user.id}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if SIGNAL_CHAT_ID:
            try: await context.bot.send_message(chat_id=SIGNAL_CHAT_ID, text=support_payload, parse_mode="Markdown", reply_markup=reply_markup)
            except Exception: await context.bot.send_message(chat_id=SIGNAL_CHAT_ID, text=support_payload, reply_markup=reply_markup)
            await update.message.reply_text("✅ **تم إرسال رسالتك وتوجيهها فوراً لغرفة عمليات الوكالة، سيتم الرد عليك دغري الحين يا وحش!**")
        else:
            await update.message.reply_text("⚠️ خطأ صيانة: جروب الاستقبال غير مفعل الحين، يرجى كتابة `/setup_signals` بالجروب أولاً.")
        return

    if context.user_data.get('awaiting_id'):
        context.user_data['awaiting_id'] = False
        user = update.effective_user
        username = f"@{user.username}" if user.username else "لا يوجد يوزرنيم"
        
        db = load_user_data()
        db[str(user_id)] = {
            "status": "PENDING",
            "total_used": db.get(str(user_id), {}).get("total_used", 3),
            "week_used": 3,
            "week_start": db.get(str(user_id), {}).get("week_start", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            "partner_id": text
        }
        save_user_data(db)
        
        admin_payload = (
            f"📥 **طلب انضمام وتفعيل حساب وكالة جديد الحين!** 📥\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 **اسم العميل:** {user.first_name}\n"
            f"🆔 **معرفه الرقمي للتيليجرام:** `{user.id}`\n"
            f"🎭 **اليوزرنيم مالت الحساب:** {username}\n"
            f"🔑 **الـ Partner Account ID المرسل:** `{text}`\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"💡 *وظيفة الإدارة الحين:* افحص لوحة تحكم JustMarkets وتأكد من وجود هذا الآي دي، ثم اضغط على أحد الزرين بالأسفل للاعتماد أو الرفض فوراً دغري الحين الحين!"
        )
        
        keyboard = [
            [InlineKeyboardButton("🟢 تأكيد واعتماد VIP", callback_data=f"approve_{user_id}"),
             InlineKeyboardButton("🔴 رفض الطلب", callback_data=f"reject_{user_id}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if SIGNAL_CHAT_ID:
            try: await context.bot.send_message(chat_id=SIGNAL_CHAT_ID, text=admin_payload, parse_mode="Markdown", reply_markup=reply_markup)
            except Exception: await context.bot.send_message(chat_id=SIGNAL_CHAT_ID, text=admin_payload, reply_markup=reply_markup)
            await update.message.reply_text("✅ **تم رفع الـ ID مالتك لغرفة مراجعة الإدارة بنجاح! جاري فحص حسابك وتفعيله الحين مدى الحياة، انتظر إشعار القبول الفوري الحين بالخاص.**")
        else:
            await update.message.reply_text("⚠️ خطأ إدارة: يرجى تفعيل معرف الاستقبال أولاً عبر كود السيرفر.")
        return

    if "طلب صفقة مضاربة" in text:
        await update.message.reply_text("⚠️ **ليدر! يرجى إرسال لقطة شاشة واضحة كلياً ونظيفة من منصة TradingView حصراً على الفريم المطلوب الحين (صورة عادية أو كملف Document) لتجنب رفض الطلب من عيون المحرك الحين.** 📈")
        
    elif "Just Martink" in text or "VIP" in text:
        await update.message.reply_text(
            "👑 **بوابة اشتراكات VIP المعتمدة - وكالة Just Martink العالمية** 👑\n\n"
            "🔥 انضم الآن لصندوق العمليات الكبرى واستفد من البث الآلي المستمر على مدار الساعة بدون أي لاق أو أخطاء!\n\n"
            "💼 **شروط وخطط الاعتماد بالوكالة مالتنا الحين:**\n"
            "🔗 **رابط الوكالة المباشر للتسجيل:** https://one.justmarkets.link/a/tr42sl0svg\n"
            "🔑 **Partner Code:** `tr42sl0svg`\n\n"
            "📞 بعد التسجيل، اضغط على زر **(📞 الدعم الفني المباشر)** واكتب رقم الـ ID مالت حسابك الجديد، وسيتم تفعيل حسابك في السيرفر مدى الحياة فوراً وبدون أي قيود الحين!",
            parse_mode="Markdown"
        )
        
    elif "الدعم الفني" in text:
        context.user_data['awaiting_support'] = True
        await update.message.reply_text("📝 **يا مرحب بك يا ليدر! اكتب رسالتك أو مشكلتك الفنية الحين في سطر واحد وأرسلها، وسيتم رفعها فوراً لغرفة عمليات الوكالة...**")

if __name__ == '__main__':
    threading.Thread(target=run_flask_server, daemon=True).start()
    TOKEN = os.environ.get("BOT_TOKEN", "8518436165:AAH2-DjOv0lh9EPpeatvKhAIX-1ODvvvIfY")
    application = Application.builder().token(TOKEN).post_init(post_init).build()
    
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("setup_signals", setup_signals_command))
    application.add_handler(CommandHandler("scan_now", scan_now_command))
    application.add_handler(CallbackQueryHandler(handle_callback_queries))
    application.add_handler(MessageHandler(filters.PHOTO, handle_chart_photo))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_chart_document))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_buttons))
    application.run_polling()
