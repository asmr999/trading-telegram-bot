import os
import base64
import requests

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
SAMBANOVA_API_KEY = os.environ.get("SAMBANOVA_API_KEY")
COHERE_API_KEY = os.environ.get("COHERE_API_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

INSTITUTIONAL_PROMPT = (
    "أنت رئيس اللجنة الفنية العليا لإدارة السيولة بصندوق SmartEntry العالمي.\n"
    "يُمنع منعاً باتاً كتابة أي مقدمات أو فقرات إنشائية أو الإشارة لشركات الذكاء الاصطناعي نهائياً.\n"
    "صغ التقرير بناءً على قراءة خبراء ماليين في نقاط جافة ومباشرة للمتداول الحين كالتالي حصراً:\n"
    "1. نوع الأداة والفريم M5 أو M15 أو H1 المكتشف بوضوح.\n"
    "2. اتجاه الحركة اللحظي الصارم: اكتب حصراً أحد العناوين الثلاثة التالية في سطر منفصل وبخط عريض: "
    "[🟢 شراء BUY] أو [🔴 بيع SELL] أو [🟡 انتظار عند وصول السعر WAIT].\n"
    "3. 🎯 نسبة نجاح الصفقة المتوقعة فَنياً: حدد نسبة مئوية دقيقة بناءً على قوة النموذج وحجم السيولة (مثال: 🔥 نسبة النجاح المتوقعة: 88%).\n"
    "4. سعر الدخول (Entry Price): حدد ما إذا كان الدخول لحظياً فورياً الحين أو توقع خبراء شايفين إنه يستنى السعر المناسب ويضع أمراً معلقاً (Pending Order: Limit/Stop).\n"
    "5. جني الأرباح التصاعدي الفني الحين: الهدف 1، الهدف 2، الهدف 3.\n"
    "6. وقف الخسارة الصارم (Stop Loss) بما يضمن إدارة مخاطر 1:2 بالملّي.\n"
    "7. قاعدة أمان إدارة الصفقة: (عند ضرب الهدف الأول، يتم نقل وقف الخسارة فوراً إلى نقطة الدخول لتأمين الصفقة الحين كلياً).\n"
    "8. ⚠️ ملاحظة قوية للتحليل المرسل: تنبيه صارم بخصوص إدارة رأس المال وحتمية الالتزام بالاستوب لوز لحماية المحفظة من انعكاسات السيولة المفاجئة الحين.\n\n"
    "اسم المنصة الخاص بنا: منصتنا الخاصة بتحليل أمهر الخبراء الماليين الحين."
)

AGENCY_SIGNATURE = (
    "\n━━━━━━━━━━━━━━━━━━━━━━━━\n"
    "👑 **صادر برعاية المحفظة المؤسسية الكبرى** 👑\n"
    "💼 **وكالة جَست مارتنك العالمية | Just Martink Agency**\n"
    "🔗 **رابط التسجيل والوكالة مالتنا الحين:** https://one.justmarkets.link/a/tr42sl0svg\n"
    "🔑 **Partner Code:** `tr42sl0svg`"
)

# ✅ الموديلات النصية الحالية عند Groq (llama-3.3-70b-versatile تم إيقافه بتاريخ 17 يونيو 2026)
GROQ_TEXT_MODEL = "openai/gpt-oss-120b"
# ✅ الموديل البصري الحالي عند Groq (llama-3.2-11b-vision-preview متوقف من زمان)
GROQ_VISION_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"

# 🔒 برومبت خاص بالإدارة فقط: يمنع الموديل من اختراع أي رقم، ويلزمه يستخدم الأرقام
# المحسوبة رياضياً فقط. هذا للاستخدام الداخلي للإدارة، وليس توصية جاهزة للنشر.
ADMIN_ONLY_PROMPT = (
    "أنت محلل فني تابع لغرفة عمليات داخلية. هذا التحليل يطّلع عليه عضو إدارة أولاً، وهو من يقرر "
    "لاحقاً (بضغطة زر منفصلة) هل ينشره لمجموعة الـ VIP أو يرفضه - أنت لا تقرر النشر ولا تخاطب العميل مباشرة.\n"
    "معك أرقام مؤشرات فنية حقيقية محسوبة رياضياً من بيانات السوق الفعلية (RSI, EMA, MACD).\n"
    "قواعد صارمة يجب الالتزام بها:\n"
    "1. ممنوع اختراع أي نسبة نجاح أو رقم غير موجود بالمعطيات المرسلة لك. استخدم فقط 'درجة التوافق الفني' "
    "الممررة لك كما هي بدون تعديل، واذكرها كـ'درجة توافق فني' وليس 'نسبة نجاح مضمونة'.\n"
    "2. اشرح بإيجاز لماذا الاتجاه المحسوب (BUY/SELL/WAIT) طلع كذا بالاعتماد على المؤشرات المعطاة فقط.\n"
    "3. اقترح مستوى دخول ووقف خسارة وأهداف منطقية بناءً على السعر الحالي والتذبذب، مع ذكر إنها اقتراحات "
    "وليست ضمانات.\n"
    "4. اختم بجملة قصيرة تذكّر بمخاطر التداول وأن لا شيء مضمون بالأسواق.\n"
    "5. ممنوع أي مقدمات تسويقية أو ذكر جهات تسويق أو روابط - هذا الجزء تتكفل به الإدارة يدوياً إذا قررت النشر."
)


def generate_admin_technical_report(indicators_text):
    """
    تقرير داخلي للإدارة فقط: يعتمد كلياً على أرقام محسوبة رياضياً (indicators.py)
    ويُطلب من الموديل تفسيرها فقط - بدون اختراع أي نسبة جديدة، وبدون توقيع تسويقي VIP.
    """
    full_prompt = f"{ADMIN_ONLY_PROMPT}\n\n[الأرقام المحسوبة فعلياً]:\n{indicators_text}"

    if GEMINI_API_KEY:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
            payload = {
                "contents": [{"parts": [{"text": full_prompt}]}],
                "generationConfig": {"temperature": 0.0}
            }
            res = requests.post(url, json=payload, headers={'Content-Type': 'application/json'}, timeout=15)
            if res.status_code == 200:
                candidates = res.json().get('candidates', [])
                if candidates:
                    parts = candidates[0].get('content', {}).get('parts', [])
                    if parts and parts[0].get('text'):
                        return parts[0]['text']
            else:
                print(f"🚨 [Gemini-admin] كود: {res.status_code} | {res.text[:300]}")
        except Exception as e:
            print(f"❌ [Gemini-admin] كراش: {str(e)}")

    if GROQ_API_KEY:
        try:
            res = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                json={"model": GROQ_TEXT_MODEL, "messages": [{"role": "user", "content": full_prompt}], "temperature": 0.0},
                headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
                timeout=15
            )
            if res.status_code == 200:
                choices = res.json().get('choices', [])
                if choices:
                    content = choices[0].get('message', {}).get('content', '')
                    if content:
                        return content
            else:
                print(f"🚨 [Groq-admin] كود: {res.status_code} | {res.text[:300]}")
        except Exception as e:
            print(f"❌ [Groq-admin] كراش: {str(e)}")

    return "❌ تعذر توليد التقرير الداخلي الآن، حاول مرة أخرى."


def fetch_model_stance_and_text(provider, url, headers, payload, response_type="openai"):
    try:
        res = requests.post(url, json=payload, headers=headers, timeout=12)
        if res.status_code == 200:
            res_data = res.json()
            if response_type == "openai":
                choices = res_data.get('choices', [])
                content = choices[0].get('message', {}).get('content', '') if choices else ''
            else:
                content = res_data.get('text', '')

            if content:
                stance = "HOLD"
                if "شراء" in content or "BUY" in content.upper(): stance = "BUY"
                elif "بيع" in content or "SELL" in content.upper(): stance = "SELL"
                return stance, content
        else:
            print(f"🚨 [{provider}] فشل الطلب - كود: {res.status_code} | الرد: {res.text[:300]}")
    except Exception as e:
        print(f"❌ [{provider}] كراش داخلي: {str(e)}")
    return None, None


def analyze_market_data_text(indicators_text):
    votes = {"BUY": 0, "SELL": 0, "HOLD": 0}
    collected_reports = []

    full_prompt = (
        f"{INSTITUTIONAL_PROMPT}\n\n"
        f"[المعطيات الرقمية المفلترة لسعر السوق الحالي الحين]:\n{indicators_text}"
    )

    if GEMINI_API_KEY:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
            payload = {
                "contents": [{"parts": [{"text": full_prompt}]}],
                "generationConfig": {"temperature": 0.0}
            }
            res = requests.post(url, json=payload, headers={'Content-Type': 'application/json'}, timeout=15)
            if res.status_code == 200:
                res_json = res.json()
                candidates = res_json.get('candidates', [])
                if candidates:
                    parts = candidates[0].get('content', {}).get('parts', [])
                    if parts:
                        report = parts[0].get('text', '')
                        if report:
                            return report + AGENCY_SIGNATURE
            else:
                print(f"🚨 [Gemini-text] فشل الطلب - كود: {res.status_code} | الرد: {res.text[:300]}")
        except Exception as e:
            print(f"❌ [Gemini-text] كراش داخلي: {str(e)}")

    if GROQ_API_KEY:
        s, t = fetch_model_stance_and_text(
            "Groq",
            "https://api.groq.com/openai/v1/chat/completions",
            {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
            {"model": GROQ_TEXT_MODEL, "messages": [{"role": "user", "content": full_prompt}], "temperature": 0.0}
        )
        if s: votes[s] += 1; collected_reports.append(t)

    if not collected_reports:
        return "❌ خطأ فني الحين: السيرفرات الرقمية تحت صيانة سريعة، يرجى إعادة المحاولة الحين."

    final_decision = max(votes, key=votes.get)
    best_report = collected_reports[0]
    for report in collected_reports:
        if final_decision == "BUY" and ("شراء" in report or "هدف" in report):
            best_report = report
            break
        elif final_decision == "SELL" and ("بيع" in report or "مقاومة" in report):
            best_report = report
            break

    clean_report = best_report.replace("Groq", "").replace("OpenAI", "").replace("Gemini", "").replace("Llama", "")
    return clean_report + AGENCY_SIGNATURE


def analyze_chart_image(image_bytes, mime_type="image/jpeg"):
    """👁️ فحص البث البصري - يدعم اكتشاف نوع الصورة الفعلي بدل افتراض jpeg دايماً"""
    image_base64 = base64.b64encode(image_bytes).decode('utf-8')

    # لو النوع الممرر مو من نوع صورة معروف، رجّعه لـ jpeg كقيمة افتراضية آمنة
    if mime_type not in ("image/jpeg", "image/png", "image/webp", "image/heic", "image/heif"):
        mime_type = "image/jpeg"

    vision_prompt = (
        f"{INSTITUTIONAL_PROMPT}\n\n"
        "أمامك الآن صورة شارت حية من TradingView أرسلها العميل. انظر بدقة فائقة وبدون أي أخطاء نهائياً للأركان التالية الحين:\n"
        "1. حدد اسم الأداة والفريم بوضوح من أعلى اليسار الحين.\n"
        "2. انظر لأعمدة حجم التداول (Volume Bars) بالأسفل لتأكد ما إذا كان الكسر حقيقياً ومسنوداً بسيولة مؤسسية، واحسب نسبة نجاح الصفقة فَنياً بناءً على وضوح الاتجاه وقوة السيولة الحين.\n"
        "3. صغ التوصية ملوكي ومفلترة لسعر السوق بالملّي: حدد الاتجاه الصافي [شراء أو بيع أو انتظار]، وضَع نسبة النجاح بوضوح، وضَع سعر الدخول لحظي أو معلق بناءً على رؤية الخبراء، "
        "واكتب الأهداف والاستوب لوز وقاعدة الأمان والملاحظة القوية الحين كلياً."
    )

    # 🟢 خط الدفاع الأول: Gemini
    if GEMINI_API_KEY:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
            payload = {
                "contents": [{
                    "parts": [
                        {"text": vision_prompt},
                        {"inlineData": {"mimeType": mime_type, "data": image_base64}}
                    ]
                }],
                "generationConfig": {"temperature": 0.0}
            }
            res = requests.post(url, json=payload, headers={'Content-Type': 'application/json'}, timeout=30)

            print(f"🚨 [رادار فحص جوجل] - كود الاستجابة: {res.status_code} | نص الرد: {res.text[:500]}")

            if res.status_code == 200:
                res_json = res.json()
                candidates = res_json.get('candidates', [])
                if candidates:
                    parts = candidates[0].get('content', {}).get('parts', [])
                    if parts:
                        text_result = parts[0].get('text', '')
                        if text_result:
                            return text_result + AGENCY_SIGNATURE
                    else:
                        print("⚠️ [Gemini] الرد رجع بدون parts - غالباً السبب finishReason غير STOP (تحقق من safety/blocked).")
                else:
                    print(f"⚠️ [Gemini] لا يوجد candidates بالرد: {res_json}")
        except Exception as e:
            print(f"❌ كراش داخلي في دالة طلب جوجل: {str(e)}")

    # 🔵 خط الدفاع الثاني: Groq Vision (llama-4-scout بدل الموديل المتوقف)
    if GROQ_API_KEY:
        try:
            url = "https://api.groq.com/openai/v1/chat/completions"
            payload = {
                "model": GROQ_VISION_MODEL,
                "messages": [{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": vision_prompt},
                        {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{image_base64}"}}
                    ]
                }],
                "temperature": 0.0
            }
            res = requests.post(url, json=payload, headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}, timeout=15)

            print(f"🚨 [رادار فحص جروك] - كود الاستجابة: {res.status_code} | نص الرد: {res.text[:500]}")

            if res.status_code == 200:
                res_data = res.json()
                choices = res_data.get('choices', [])
                if choices:
                    content = choices[0].get('message', {}).get('content', '')
                    if content:
                        return content.replace("Groq", "").replace("Llama", "") + AGENCY_SIGNATURE
        except Exception as e:
            print(f"❌ كراش داخلي في دالة طلب جروك: {str(e)}")

    return "⚠️ **تنبيه نظام الطوارئ:** لم تتمكن محركات الرؤية من فك الرموز الحين، يرجى إعادة إرسال شارت TradingView واضح كلياً الحين ثانية."
