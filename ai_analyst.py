import os
import base64
import requests

# 🔐 خزنة المفاتيح الحرة
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
SAMBANOVA_API_KEY = os.environ.get("SAMBANOVA_API_KEY")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
COHERE_API_KEY = os.environ.get("COHERE_API_KEY")

# 🎭 الميثاق المؤسسي الحصار لحجب الهوية
INSTITUTIONAL_PROMPT = (
    "أنت رئيس اللجنة الفنية العليا لإدارة المخاطر بصندوق SmartEntry الاستثماري العالمي.\n"
    "يُمنع منعاً باتاً ذكر أنك ذكاء اصطناعي أو الإشارة لأسماء شركات التكنولوجيا.\n"
    "حلل المعطيات المرفقة بدقة وجفاف رياضي وصغ التقرير بصيغة بشرية رسمية كالتالي:\n"
    "1. اتجاه السيولة الحالي الحين (شراء / بيع / انتظار).\n"
    "2. نقاط التنفيذ الفورية (سعر دخول دقيق، 3 أهداف حتمية، وقف خسارة صارم يضمن إدارة مخاطر 1:2).\n"
    "3. التبرير الهيكلي للحركة بناءً على أحزمة السيولة الحالية الحية بالسوق."
)

def fetch_model_stance_and_text(provider, url, headers, payload, response_type="openai"):
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
    """تحليل الداتا النصية الحية الحين عبر التصويت بالأغلبية"""
    votes = {"BUY": 0, "SELL": 0, "HOLD": 0}
    collected_reports = []
    full_prompt = f"{INSTITUTIONAL_PROMPT}\n\nأسعار البورصة الحية الحين:\n{indicators_text}"
    
    if GROQ_API_KEY:
        s, t = fetch_model_stance_and_text("Groq", "https://api.groq.com/openai/v1/chat/completions", {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}, {"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": full_prompt}], "temperature": 0.0})
        if s: votes[s] += 1; collected_reports.append(t)

    if SAMBANOVA_API_KEY:
        s, t = fetch_model_stance_and_text("SambaNova", "https://api.sambanova.ai/v1/chat/completions", {"Authorization": f"Bearer {SAMBANOVA_API_KEY}", "Content-Type": "application/json"}, {"model": "Meta-Llama-3.1-70B-Instruct", "messages": [{"role": "user", "content": full_prompt}], "temperature": 0.0})
        if s: votes[s] += 1; collected_reports.append(t)

    if OPENROUTER_API_KEY:
        s, t = fetch_model_stance_and_text("OpenRouter", "https://openrouter.ai/api/v1/chat/completions", {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json", "HTTP-Referer": "https://smartentry.global", "X-Title": "SmartEntry"}, {"model": "meta-llama/llama-3.1-8b-instruct:free", "messages": [{"role": "user", "content": full_prompt}], "temperature": 0.0})
        if s: votes[s] += 1; collected_reports.append(t)

    if COHERE_API_KEY:
        s, t = fetch_model_stance_and_text("Cohere", "https://api.cohere.com/v1/chat", {"Authorization": f"Bearer {COHERE_API_KEY}", "Content-Type": "application/json"}, {"model": "command-r-plus", "message": full_prompt, "temperature": 0.0}, response_type="cohere")
        if s: votes[s] += 1; collected_reports.append(t)

    if not collected_reports:
        return "⚠️ **[تنبيه]:** خوادم الفرز النصي ممتلئة حالياً الحين، يرجى إعادة طلب الأمر."

    final_decision = max(votes, key=votes.get)
    total_active_votes = sum(votes.values())
    best_report = collected_reports[0]
    for report in collected_reports:
        if final_decision == "BUY" and ("شراء" in report or "هدف" in report):
            best_report = report
            break
        elif final_decision == "SELL" and ("بيع" in report or "مقاومة" in report):
            best_report = report
            break

    clean_report = best_report.replace("Groq", "").replace("OpenAI", "").replace("Gemini", "").replace("ChatGPT", "").replace("Llama", "")
    return (
        f"👑 **SmartEntry Global | قسم المقاصة الرقمية** 👑\n"
        f"📋 **التقرير الفني المشترك الصادر الحين**\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🗳️ *تصويت خبراء الصندوق الحين:* (شراء: {votes['BUY']} | بيع: {votes['SELL']} | انتظار: {votes['HOLD']}) بنسبة حسم: {int((votes[final_decision]/total_active_votes)*100)}%\n\n"
        f"{clean_report}"
    )

def analyze_chart_image(image_bytes):
    """👁️ التحليل البصري المباشر 100%: قراءة صورة الشارت وإصدار التقرير والصفقة فوراً وبدون وسيط نصي!"""
    image_base64 = base64.b64encode(image_bytes).decode('utf-8')
    
    # صياغة الأمر البصري المباشر والمشدد لاستخراج صفقة حقيقية من الشارت نفسه
    vision_prompt = (
        f"{INSTITUTIONAL_PROMPT}\n\n"
        "أمامك الآن صورة شارت حية وحقيقية من شاشة المتداول. انظر بعينك البصرية بدقة للشموع اليابانية، "
        "والاتجاه الحالي، وخطوط الدعم والمقاومة المرسومة، واستخرج الصفقة الفورية الصافية الحين بدون أي لف أو دوران وبأعلى دقة فنية."
    )

    # 1️⃣ المحرك البصري الأول المباشر: Groq Vision
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
                report = res.json()['choices'][0]['message']['content']
                return f"👑 **SmartEntry Global | وحدة التحليل البصري المباشر (الأساسي)** 👑\n\n" + report.replace("Groq", "").replace("Llama", "")
        except Exception: pass

    # 2️⃣ المحرك البصري الاحتياطي المباشر: OpenRouter Vision
    if OPENROUTER_API_KEY:
        try:
            url = "https://openrouter.ai/api/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json",
                "HTTP-Referer": "https://smartentry.global", "X-Title": "SmartEntry"
            }
            payload = {
                "model": "meta-llama/llama-3.2-11b-vision-instruct:free",
                "messages": [{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": vision_prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
                    ]
                }],
                "temperature": 0.0
            }
            res = requests.post(url, json=payload, headers=headers, timeout=15)
            if res.status_code == 200:
                report = res.json()['choices'][0]['message']['content']
                return f"👑 **SmartEntry Global | وحدة التحليل البصري المباشر (الاحتياطي)** 👑\n\n" + report.replace("Groq", "").replace("Llama", "")
        except Exception: pass

    return "❌ **تنبيه أمني:** لم تتمكن محركات الرؤية المباشرة من فك رموز الصورة الحين. يرجى التأكد من صلاحية المفاتيح المجانية في سيرفر ريندر."
