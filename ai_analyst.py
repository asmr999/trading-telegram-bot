import os
import base64
import requests

# 🔐 خزنة المفاتيح الحرة والمؤمنة لعام 2026
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
SAMBANOVA_API_KEY = os.environ.get("SAMBANOVA_API_KEY")
COHERE_API_KEY = os.environ.get("COHERE_API_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

# 🎭 ميثاق الاختصار الصارم لمنع الحشو وطباعة الصافي الفوري الحين
INSTITUTIONAL_PROMPT = (
    "أنت رئيس اللجنة الفنية العليا لإدارة السيولة بصندوق SmartEntry العالمي.\n"
    "يُمنع منعاً باتاً كتابة أي مقدمات أو فقرات إنشائية أو الإشارة لشركات الذكاء الاصطناعي.\n"
    "صغ التقرير في نقاط جافة ومباشرة للمتداول الحين كالتالي حصراً:\n"
    "1. نوع الأداة والفريم المكتشف (مثال: الذهب XAUUSD | فريم 15 دقيقة).\n"
    "2. اتجاه الحركة اللحظي (شراء BUY أو بيع SELL أو انتظار HOLD).\n"
    "3. نقطة الدخول الصافية (Entry Price).\n"
    "4. جني الأرباح التصاعدي: الهدف 1، الهدف 2، الهدف 3.\n"
    "5. وقف الخسارة الصارم (Stop Loss).\n"
    "6. قاعدة أمان إدارة الصفقة: (عند ضرب الهدف الأول، يتم نقل وقف الخسارة فوراً إلى نقطة الدخول لتأمين الصفقة الحين كلياً)."
)

# 🔥 حقن رابط وكالتك الحقيقي والـ Partner Code مالتك بالملّي الحين لضمان العمولات دغري
AGENCY_SIGNATURE = (
    "\n━━━━━━━━━━━━━━━━━━━━━━━━\n"
    "👑 **صادر برعاية المحفظة المؤسسية الكبرى** 👑\n"
    "💼 **وكالة جَست مارتنك العالمية | Just Martink Agency**\n"
    "🔗 **رابط التسجيل والوكالة مالتنا الحين:** https://one.justmarkets.link/a/tr42sl0svg\n"
    "🔑 **Partner Code:** `tr42sl0svg`"
)

def fetch_model_stance_and_text(provider, url, headers, payload, response_type="openai"):
    try:
        res = requests.post(url, json=payload, headers=headers, timeout=10)
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
    full_prompt = f"{INSTITUTIONAL_PROMPT}\n\nأسعار البورصة الحية الحين:\n{indicators_text}"
    
    if GROQ_API_KEY:
        s, t = fetch_model_stance_and_text("Groq", "https://api.groq.com/openai/v1/chat/completions", {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}, {"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": full_prompt}], "temperature": 0.0})
        if s: votes[s] += 1; collected_reports.append(t)

    if SAMBANOVA_API_KEY:
        s, t = fetch_model_stance_and_text("SambaNova", "https://api.sambanova.ai/v1/chat/completions", {"Authorization": f"Bearer {SAMBANOVA_API_KEY}", "Content-Type": "application/json"}, {"model": "Meta-Llama-3.1-70B-Instruct", "messages": [{"role": "user", "content": full_prompt}], "temperature": 0.0})
        if s: votes[s] += 1; collected_reports.append(t)

    if COHERE_API_KEY:
        s, t = fetch_model_stance_and_text("Cohere", "https://api.cohere.com/v1/chat", {"Authorization": f"Bearer {COHERE_API_KEY}", "Content-Type": "application/json"}, {"model": "command-r-plus", "message": full_prompt, "temperature": 0.0}, response_type="cohere")
        if s: votes[s] += 1; collected_reports.append(t)

    if not collected_reports:
        return "⚠️ **[تنبيه]:** خوادم الفرز ممتلئة حالياً الحين، يرجى إعادة طلب الأمر."

    final_decision = max(votes, key=votes.get)
    best_report = collected_reports[0]
    for report in collected_reports:
        if final_decision == "BUY" and ("شراء" in report or "هدف" in report):
            best_report = report
            break
        elif final_decision == "SELL" and ("بيع" in report or "مقاومة" in report):
            best_report = report
            break

    clean_report = best_report.replace("Groq", "").replace("OpenAI", "").replace("Gemini", "").replace("ChatGPT", "").replace("Llama", "")
    return clean_report + AGENCY_SIGNATURE

def analyze_chart_image(image_bytes):
    """👁️ العين البصرية الجبارة: تحليل الفريم وأعمدة الفوليوم لعام 2026 مع شلال طوارئ تلقائي"""
    image_base64 = base64.b64encode(image_bytes).decode('utf-8')
    
    vision_prompt = (
        "You are the Head of Technical Analysis at SmartEntry Global Fund.\n"
        "Look carefully at this financial chart image from the user's mobile.\n"
        "1. Detect the timeframe from the top left corner (M5, M15, M30, H1).\n"
        "2. Look at the volume bars at the bottom of the chart to confirm institutional momentum.\n"
        "Formulate a strict, direct, and zero-fluff trading signal in Arabic. Provide exactly:\n"
        "1. Detected Asset & Timeframe\n"
        "2. Action (BUY / SELL / WAIT)\n"
        "3. Exact Entry Price\n"
        "4. Target 1, Target 2, Target 3\n"
        "5. Tight Stop-Loss matching 1:2 risk/reward ratio\n"
        "6. Management rule: (عند ضرب الهدف الأول، يتم نقل وقف الخسارة فوراً إلى نقطة الدخول لتأمين الأرباح الحين).\n"
        "Do not write any long paragraphs or introductions. Just bullets."
    )

    # 1️⃣ خط الدفاع الأول: وحش جيميناي الحديث المستقر لعام 2026
    if GEMINI_API_KEY:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
            payload = {
                "contents": [{
                    "parts": [
                        {"text": vision_prompt},
                        {"inlineData": {"mimeType": "image/jpeg", "data": image_base64}}
                    ]
                }],
                "generationConfig": {"temperature": 0.0}
            }
            res = requests.post(url, json=payload, headers={'Content-Type': 'application/json'}, timeout=30)
            if res.status_code == 200:
                res_json = res.json()
                if 'candidates' in res_json and len(res_json['candidates']) > 0:
                    report = res_json['candidates'][0]['content']['parts'][0]['text']
                    return report + AGENCY_SIGNATURE
        except Exception: pass

    # 2️⃣ خط الدفاع الثاني الاحتياطي: جروك البصري السريع (Groq Vision)
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
                return report.replace("Groq", "").replace("Llama", "") + AGENCY_SIGNATURE
        except Exception: pass

    return "⚠️ **تنبيه المحرك:** السيرفرات مشغولة الحين، يرجى إرسال الشارت بعد ثوانٍ قليلة."
