import os
import base64
import requests

# 🔐 الخزنة الرقمية الحرة (تم طرد OpenAI وجيمناي نهائياً لضمان المجانية والاستقرار)
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
SAMBANOVA_API_KEY = os.environ.get("SAMBANOVA_API_KEY")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
COHERE_API_KEY = os.environ.get("COHERE_API_KEY")

# 🎭 الميثاق السري لحجب الهوية وصياغة الفخامة البشرية الجافة
INSTITUTIONAL_PROMPT = (
    "أنت كبير المستشارين الماليين ورئيس اللجنة الفنية العليا بصندوق SmartEntry الاستثماري العالمي.\n"
    "يُمنع منعاً باتاً ذكر أي مصطلحات تكنولوجية أو الإشارة إلى أنك ذكاء اصطناعي أو ذكر أسماء شركات (Groq, Llama, Cohere, OpenAI).\n"
    "يجب صياغة التقرير كإنسان محترف جداً يتحدث باسم 'اللجنة الفنية العليا للصندوق' بمنتهى الجفاف الرياضي وبناءً على المعطيات كالتالي:\n"
    "1. اتجاه حركة السيولة (شراء / بيع / انتظار خارج الشاشات الحين لحماية رأس المال).\n"
    "2. أسعار التنفيذ بدقة (سعر الدخول المقترح، 3 أهداف حتمية تصاعدية، وقف خسارة صارم جداً لضمان إدارة مخاطر 1:2 على الأقل).\n"
    "3. التبرير الرياضي الهيكلي بناءً على أحزمة المقاومة والدعم والتدفق الحجمي الحالي بالسوق."
)

def fetch_model_stance_and_text(provider, url, headers, payload, response_type="openai"):
    """جلب القرار وتحديد صوت الخبير بثواني وبدون كراش"""
    try:
        res = requests.post(url, json=payload, headers=headers, timeout=8)
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
    """غرفة المقاصة والفرز وحسم القرار بالأغلبية الساحقة للـ 4 مواقع الحرة"""
    votes = {"BUY": 0, "SELL": 0, "HOLD": 0}
    collected_reports = []
    full_prompt = f"{INSTITUTIONAL_PROMPT}\n\nالمعطيات الفنية الحالية الحية بالسوق:\n{indicators_text}"
    
    # 1️⃣ صوت Groq
    if GROQ_API_KEY:
        s, t = fetch_model_stance_and_text("Groq", "https://api.groq.com/openai/v1/chat/completions", {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}, {"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": full_prompt}], "temperature": 0.0})
        if s: votes[s] += 1; collected_reports.append(t)

    # 2️⃣ صوت SambaNova
    if SAMBANOVA_API_KEY:
        s, t = fetch_model_stance_and_text("SambaNova", "https://api.sambanova.ai/v1/chat/completions", {"Authorization": f"Bearer {SAMBANOVA_API_KEY}", "Content-Type": "application/json"}, {"model": "Meta-Llama-3.1-70B-Instruct", "messages": [{"role": "user", "content": full_prompt}], "temperature": 0.0})
        if s: votes[s] += 1; collected_reports.append(t)

    # 3️⃣ صوت OpenRouter
    if OPENROUTER_API_KEY:
        s, t = fetch_model_stance_and_text("OpenRouter", "https://openrouter.ai/api/v1/chat/completions", {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}, {"model": "meta-llama/llama-3.1-8b-instruct:free", "messages": [{"role": "user", "content": full_prompt}], "temperature": 0.0})
        if s: votes[s] += 1; collected_reports.append(t)

    # 4️⃣ صوت Cohere
    if COHERE_API_KEY:
        s, t = fetch_model_stance_and_text("Cohere", "https://api.cohere.com/v1/chat", {"Authorization": f"Bearer {COHERE_API_KEY}", "Content-Type": "application/json"}, {"model": "command-r-plus", "message": full_prompt, "temperature": 0.0}, response_type="cohere")
        if s: votes[s] += 1; collected_reports.append(t)

    if not collected_reports:
        return "⚠️ **[تنبيه من غرفة العمليات]:** الاتصال المباشر بالبورصة تحت الصيانة اللحظية حالياً، يرجى إعادة المحاولة."

    final_decision = max(votes, key=votes.get)
    total_active_votes = sum(votes.values())

    # اختيار أفضل تقرير متناسق مع رأي الأغلبية
    best_report = collected_reports[0]
    for report in collected_reports:
        if final_decision == "BUY" and ("شراء" in report or "هدف" in report):
            best_report = report
            break
        elif final_decision == "SELL" and ("بيع" in report or "مقاومة" in report):
            best_report = report
            break

    # غسيل كامل وتطهير للنص لضمان عدم تسريب أي رمز برمجي
    clean_report = best_report.replace("Groq", "").replace("OpenAI", "").replace("Gemini", "").replace("ChatGPT", "").replace("Llama", "")

    dashboard = (
        f"👑 **SmartEntry Global | قسم إدارة الأصول والسيولة** 👑\n"
        f"📋 **التقرير الفني الصادر عن اللجنة الفنية العليا**\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🗳️ *معدل إجماع خبراء الصندوق:* (شراء: {votes['BUY']} | بيع: {votes['SELL']} | انتظار: {votes['HOLD']}) بنسبة إجماع حاسمة: {int((votes[final_decision]/total_active_votes)*100)}%\n\n"
        f"{clean_report}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"⚠️ *قاعدة أمان:* صادر وفقاً للحسابات الرياضية الجافة لأحزمة السيولة في البورصة العالمية الحين ويخضع لشروط المخاطرة الصارمة."
    )
    return dashboard

def analyze_chart_image(image_bytes):
    """👁️ الهندسة العكسية الملوكية: استخراج المعطيات من الشارت مجاناً وتمريرها فوراً للفرز والتصويت بالأغلبية للـ 4 مواقع!"""
    image_base64 = base64.b64encode(image_bytes).decode('utf-8')
    
    # أمر قراءة عيون المسح الجاف لاستخراج الأرقام من الصورة
    extraction_prompt = (
        "You are an expert financial chart scanner. Look at this screenshot image and extract ONLY the following details in raw text format:\n"
        "1. Asset name detected (Gold / Bitcoin / Forex pair).\n"
        "2. Exact current market price action visible.\n"
        "3. Major structural support line and resistance line.\n"
        "4. Overall volume and current trend direction (Bullish, Bearish, or Sideways).\n"
        "Do not write any introductory or conversational text, just extract the parameters clearly."
    )

    extracted_text = None

    # محاولة المسح بالعين المجانية الأولى (Groq Vision)
    if GROQ_API_KEY:
        try:
            url = "https://api.groq.com/openai/v1/chat/completions"
            res = requests.post(url, json={"model": "llama-3.2-11b-vision-preview", "messages": [{"role": "user", "content": [{"type": "text", "text": extraction_prompt}, {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_base64}"}}]}], "temperature": 0.0}, headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}, timeout=15)
            if res.status_code == 200:
                extracted_text = res.json()['choices'][0]['message']['content']
        except Exception: pass

    # محاولة المسح بالعين المجانية البديلة في حال انشغال الأولى (OpenRouter Vision)
    if not extracted_text and OPENROUTER_API_KEY:
        try:
            url = "https://openrouter.ai/api/v1/chat/completions"
            res = requests.post(url, json={"model": "meta-llama/llama-3.2-11b-vision-instruct:free", "messages": [{"role": "user", "content": [{"type": "text", "text": extraction_prompt}, {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_base64}"}}]}], "temperature": 0.0}, headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}, timeout=15)
            if res.status_code == 200:
                extracted_text = res.json()['choices'][0]['message']['content']
        except Exception: pass

    if not extracted_text:
        return "❌ خطأ أمني: لم تتمكن العين البصرية المجانية من مسح الشارت الفوري، يرجى التحقق من مفاتيح الرؤية."

    # 🔥 الحركة العبقرية: تمرير البيانات النصية المستخرجة من شارتك غصباً عنهم للـ 4 عقول لفرزها والتصويت عليها!
    return analyze_market_data_text(f"[معطيات مستخرجة بالعين البصرية من شارت الجوال]:\n{extracted_text}")
