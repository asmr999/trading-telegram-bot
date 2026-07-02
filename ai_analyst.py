import os
import base64
import requests

# خزنة المفاتيح الحرة والمؤمنة لعام 2026
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
SAMBANOVA_API_KEY = os.environ.get("SAMBANOVA_API_KEY")
COHERE_API_KEY = os.environ.get("COHERE_API_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# ميثاق الاختصار الصارم الحين والموجه لأمهر الخبراء الماليين
INSTITUTIONAL_PROMPT = (
    "أنت رئيس اللجنة الفنية العليا لإدارة السيولة بصندوق SmartEntry العالمي.\n"
    "يُمنع منعاً باتاً كتابة أي مقدمات أو فقرات إنشائية أو الإشارة لشركات الذكاء الاصطناعي نهائياً.\n"
    "صغ التقرير بناءً على قراءة خبراء ماليين في نقاط جافة ومباشرة للمتداول الحين كالتالي حصراً:\n"
    "1. نوع الأداة والفريم المكتشف (مثال: الذهب XAUUSD | فريم 15 دقيقة).\n"
    "2. اتجاه الحركة اللحظي الصارم: اكتب حصراً أحد العناوين الثلاثة التالية في سطر منفصل وبخط عريض: "
    "[🟢 شراء BUY] أو [🔴 بيع SELL] أو [🟡 انتظار عند وصول السعر WAIT].\n"
    "3. سعر الدخول (Entry Price): حدد ما إذا كان الدخول لحظياً فورياً الحين أو توقع خبراء شايفين إنه يستنى السعر المناسب ويضع أمراً معلقاً (Pending Order: Limit/Stop).\n"
    "4. جني الأرباح التصاعدي الفني الحين: الهدف 1، الهدف 2، الهدف 3.\n"
    "5. وقف الخسارة الصارم (Stop Loss) بما يضمن إدارة مخاطر 1:2 بالملّي.\n"
    "6. قاعدة أمان إدارة الصفقة: (عند ضرب الهدف الأول، يتم نقل وقف الخسارة فوراً إلى نقطة الدخول لتأمين الصفقة الحين كلياً).\n"
    "7. ⚠️ ملاحظة قوية للتحليل المرسل: تنبيه صارم بخصوص إدارة رأس المال وحتمية الالتزام بالاستوب لوز لحماية المحفظة من انعكاسات السيولة المفاجئة الحين.\n\n"
    "اسم المنصة الخاص بنا: منصتنا الخاصة بتحليل أمهر الخبراء الماليين الحين."
)

AGENCY_SIGNATURE = (
    "\n━━━━━━━━━━━━━━━━━━━━━━━━\n"
    "👑 **صادر برعاية المحفظة المؤسسية الكبرى** 👑\n"
    "💼 **وكالة جَست مارتنك العالمية | Just Martink Agency**\n"
    "🔗 **رابط التسجيل والوكالة مالتنا الحين:** https://one.justmarkets.link/a/tr42sl0svg\n"
    "🔑 **Partner Code:** `tr42sl0svg`"
)

def fetch_model_stance_and_text(provider, url, headers, payload, response_type="openai"):
    try:
        res = requests.post(url, json=payload, headers=headers, timeout=12)
        if res.status_code == 200:
            res_data = res.json()
            content = res_data['choices'][0]['message']['content'] if response_type == "openai" else res_data.get('text', '')
            stance = "HOLD"
            if "شراء" in content or "BUY" in content.upper(): stance = "BUY"
            elif "بيع" in content or "SELL" in content.upper(): stance = "SELL"
            return stance, content
    except Exception: pass
    return None, None

def analyze_market_data_text(indicators_text):
    votes = {"BUY": 0, "SELL": 0, "HOLD": 0}
    collected_reports = []
    
    full_prompt = (
        f"{INSTITUTIONAL_PROMPT}\n\n"
        f"[المعطيات الرقمية المفلترة لسعر السوق الحالي الحين]:\n{indicators_text}\n\n"
        f"قم بصياغة توصية فائقة الدقة وخالية من الأخطاء الفنية كلياً الحين."
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
                report = res.json()['candidates'][0]['content']['parts'][0]['text']
                return report + AGENCY_SIGNATURE
        except Exception: pass

    if GROQ_API_KEY:
        s, t = fetch_model_stance_and_text("Groq", "https://api.groq.com/openai/v1/chat/completions", {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}, {"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": full_prompt}], "temperature": 0.0})
        if s: votes[s] += 1; collected_reports.append(t)

    if SAMBANOVA_API_KEY:
        s, t = fetch_model_stance_and_text("SambaNova", "https://api.sambanova.ai/v1/chat/completions", {"Authorization": f"Bearer {SAMBANOVA_API_KEY}", "Content-Type": "application/json"}, {"model": "Meta-Llama-3.1-70B-Instruct", "messages": [{"role": "user", "content": full_prompt}], "temperature": 0.0})
        if s: votes[s] += 1; collected_reports.append(t)

    if not collected_reports:
        return "⚠️ **تنبيه فني الحين:** السيرفرات الرقمية تحت صيانة سريعة، يرجى إعادة المحاولة الحين."

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

def analyze_chart_image(image_bytes):
    image_base64 = base64.b64encode(image_bytes).decode('utf-8')
    
    vision_prompt = (
        f"{INSTITUTIONAL_PROMPT}\n\n"
        "أمامك الآن صورة شارت حية من TradingView أرسلها العميل. انظر بدقة فائقة وبدون أي أخطاء نهائياً للأركان التالية الحين:\n"
        "1. حدد اسم الأداة والفريم بوضوح من أعلى اليسار الحين.\n"
        "2. انظر لأعمدة حجم التداول (Volume Bars) بالأسفل لتأكد ما إذا كان الكسر حقيقياً ومسنوداً بسيولة مؤسسية أو فخ كاذب.\n"
        "3. صغ التوصية ملوكي ومفلترة لسعر السوق بالملّي: حدد الاتجاه الصافي [شراء أو بيع أو انتظار]، وضَع سعر الدخول لحظي أو معلق بناءً على رؤية الخبراء، "
        "واكتب الأهداف والاستوب لوز وقاعدة الأمان والملاحظة القوية الحين كلياً."
    )

    if GEMINI_API_KEY:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
            payload = {
                "contents": [{
                    "parts": [
                        {"text": vision_prompt},
                        {"inline_data": {"mime_type": "image/jpeg", "data": image_base64}}
                    ]
                }],
                "generationConfig": {"temperature": 0.0}
            }
            res = requests.post(url, json=payload, headers={'Content-Type': 'application/json'}, timeout=30)
            if res.status_code == 200:
                res_json = res.json()
                if 'candidates' in res_json and len(res_json['candidates']) > 0:
                    return res_json['candidates'][0]['content']['parts'][0]['text'] + AGENCY_SIGNATURE
        except Exception: pass

    if GROQ_API_KEY:
        try:
            url = "https://api.groq.com/openai/v1/chat/completions"
            payload = {
                "model": "llama-3.2-11b-vision-preview",
                "messages": [{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": vision_prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
                    ]
                }],
                "temperature": 0.0
            }
            res = requests.post(url, json=payload, headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}, timeout=15)
            if res.status_code == 200:
                return res.json()['choices'][0]['message']['content'].replace("Groq", "").replace("Llama", "") + AGENCY_SIGNATURE
        except Exception: pass

    return "⚠️ **تنبيه نظام الطوارئ:** لم تتمكن محركات الرؤية من فك الرموز الحين، يرجى إعادة إرسال شارت TradingView واضح كلياً الحين ثانية."
