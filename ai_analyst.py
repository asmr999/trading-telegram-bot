import os
import base64
import requests

# 🔐 جلب المفاتيح الستة الحصينة من خزنة سيرفر ريندر
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
SAMBANOVA_API_KEY = os.environ.get("SAMBANOVA_API_KEY")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
COHERE_API_KEY = os.environ.get("COHERE_API_KEY")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# 🎭 الأمر السري الصارم لحجب الهوية بالكامل وتفعيل وضع التداول المؤسسي الجاف
INSTITUTIONAL_PROMPT = (
    "أنت خبير التداول المالي الأول وعضو اللجنة الفنية العليا بصندوق SmartEntry الاستثماري العالمي.\n"
    "يُمنع منعاً باتاً الإشارة إلى أنك نموذج ذكاء اصطناعي أو برنامج أو ذكر أسماء شركات مثل (OpenAI, Gemini, Groq, Llama).\n"
    "يجب أن يتحدث الرد دائماً بصيغة 'اللجنة الفنية العليا للصندوق' أو 'قسم إدارة الأصول والسيولة'.\n"
    "مهمتك الآن: قراءة المعطيات الحية المرفقة، وصياغة التقرير الملوكي النهائي على النحو التالي وبمنتهى الجفاف الرياضي:\n"
    "1. اتجاه الحركة (شراء / بيع / انتظار خارج السوق).\n"
    "2. أسعار التنفيذ بدقة (سعر الدخول، 3 أهداف تصاعدية، وقف خسارة صارم لا يتعدى 1:2 نسبة مخاطرة).\n"
    "3. التبرير الهيكلي للحركة بناءً على أحزمة السيولة والمؤشرات الحالية الحية بالسوق."
)

def fetch_model_stance_and_text(provider, url, headers, payload, response_type="openai"):
    """دالة داخلية موحدة لضرب السيرفرات بسرعة وسحب صوت كل عقل مالي بدقة"""
    try:
        res = requests.post(url, json=payload, headers=headers, timeout=8)
        if res.status_code == 200:
            res_data = res.json()
            if response_type == "openai":
                content = res_data['choices'][0]['message']['content']
            elif response_type == "cohere":
                content = res_data.get('text', '')
            elif response_type == "gemini":
                content = res_data['candidates'][0]['content']['parts'][0]['text']
            
            # تحليل أوتوماتيكي سريع لتحديد صوت العقل (شراء، بيع، أو انتظار)
            stance = "HOLD"
            if "شراء" in content or "BUY" in content.upper():
                stance = "BUY"
            elif "بيع" in content or "SELL" in content.upper():
                stance = "SELL"
            return stance, content
    except Exception:
        pass
    return None, None

def analyze_market_data_text(indicators_text):
    """غرفة المقاصة الكبرى والتصويت بالأغلبية لـ 6 عقول مالية مع حجب الهوية"""
    
    votes = {"BUY": 0, "SELL": 0, "HOLD": 0}
    collected_reports = []
    
    # 1️⃣ عقل Groq الحاد
    if GROQ_API_KEY:
        s, t = fetch_model_stance_and_text(
            "Groq", "https://api.groq.com/openai/v1/chat/completions",
            {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
            {"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": f"{INSTITUTIONAL_PROMPT}\n\n{indicators_text}"}], "temperature": 0.0}
        )
        if s: votes[s] += 1; collected_reports.append(t)

    # 2️⃣ عقل SambaNova العملاق (مجاني وحديث)
    if SAMBANOVA_API_KEY:
        s, t = fetch_model_stance_and_text(
            "SambaNova", "https://api.sambanova.ai/v1/chat/completions",
            {"Authorization": f"Bearer {SAMBANOVA_API_KEY}", "Content-Type": "application/json"},
            {"model": "Meta-Llama-3.1-70B-Instruct", "messages": [{"role": "user", "content": f"{INSTITUTIONAL_PROMPT}\n\n{indicators_text}"}], "temperature": 0.0}
        )
        if s: votes[s] += 1; collected_reports.append(t)

    # 3️⃣ عقل OpenRouter الذكي (مجاني وحديث)
    if OPENROUTER_API_KEY:
        s, t = fetch_model_stance_and_text(
            "OpenRouter", "https://openrouter.ai/api/v1/chat/completions",
            {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"},
            {"model": "meta-llama/llama-3.1-8b-instruct:free", "messages": [{"role": "user", "content": f"{INSTITUTIONAL_PROMPT}\n\n{indicators_text}"}], "temperature": 0.0}
        )
        if s: votes[s] += 1; collected_reports.append(t)

    # 4️⃣ عقل Cohere العسكري الصارم (مجاني وحديث)
    if COHERE_API_KEY:
        s, t = fetch_model_stance_and_text(
            "Cohere", "https://api.cohere.com/v1/chat",
            {"Authorization": f"Bearer {COHERE_API_KEY}", "Content-Type": "application/json"},
            {"model": "command-r-plus", "message": f"{INSTITUTIONAL_PROMPT}\n\n{indicators_text}", "temperature": 0.0},
            response_type="cohere"
        )
        if s: votes[s] += 1; collected_reports.append(t)

    # 5️⃣ عقل OpenAI المحترف (في حال تم تفعيل الرصيد مستقبلاً)
    if OPENAI_API_KEY:
        s, t = fetch_model_stance_and_text(
            "OpenAI", "https://api.openai.com/v1/chat/completions",
            {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"},
            {"model": "gpt-4o-mini", "messages": [{"role": "user", "content": f"{INSTITUTIONAL_PROMPT}\n\n{indicators_text}"}], "temperature": 0.0}
        )
        if s: votes[s] += 1; collected_reports.append(t)

    # 6️⃣ عقل Gemini الاحتياطي المباشر
    if GEMINI_API_KEY:
        s, t = fetch_model_stance_and_text(
            "Gemini", f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}",
            {'Content-Type': 'application/json'},
            {"contents": [{"parts": [{"text": f"{INSTITUTIONAL_PROMPT}\n\n{indicators_text}"}]}], "generationConfig": {"temperature": 0.0}},
            response_type="gemini"
        )
        if s: votes[s] += 1; collected_reports.append(t)

    # ⚖️ فرز أصوات الأغلبية الساحقة وإصدار التقرير المؤسسي الحاسم
    if not collected_reports:
        return "⚠️ **[تنبيه من غرفة العمليات]:** خوادم الاتصال بالأسواق الفنية تحت الصيانة المؤقتة الحين. يرجى مراجعة إعدادات المفاتيح."

    # تحديد القرار الفائز بالأغلبية
    final_decision = max(votes, key=votes.get)
    total_active_votes = sum(votes.values())

    # تصفية وتجهيز نص التقرير الفائز بالأغلبية
    best_report = collected_reports[0]
    for report in collected_reports:
        if final_decision == "BUY" and ("شراء" in report or "هدف" in report):
            best_report = report
            break
        elif final_decision == "SELL" and ("بيع" in report or "مقاومة" in report):
            best_report = report
            break

    # تنظيف النص النهائي تجميلياً لضمان عدم وجود أي أحرف أو أسماء شركات مسربة بالخطأ
    clean_report = best_report.replace("Groq", "").replace("OpenAI", "").replace("Gemini", "").replace("ChatGPT", "")

    # بناء الهيكل الخارجي الفخم للوحة التحكم المؤسسية المحجوبة بالكامل
    dashboard = (
        f"👑 **SmartEntry Global | قسم إدارة الأصول والسيولة** 👑\n"
        f"📋 **التقرير الفني المشترك الصادر عن اللجنة الفنية العليا**\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🗳️ *إحصاء تصويت الخبراء الحين:* (شراء: {votes['BUY']} | بيع: {votes['SELL']} | انتظار: {votes['HOLD']}) ونسبة الإجماع: {int((votes[final_decision]/total_active_votes)*100)}%\n\n"
        f"{clean_report}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"⚠️ *ملاحظة صارمة:* هذا التقرير يعبر عن القراءة الرياضية الجافة لأحزمة السيولة في البورصة العالمية الحين ويخضع لقواعد إدارة المخاطر الحتمية للصندوق."
    )
    return dashboard

def analyze_chart_image(image_bytes):
    """تحليل صور الشارتات بالعين البصرية المحجوبة الهوية"""
    prompt = (
        "أنت كبير المحللين الفنيين بصندوق SmartEntry الاستثماري. حلل شارت البورصة المرفق بمنتهى الاحترافية والجفاف، "
        "واستخرج الاتجاه الفعلي للسيولة ومناطق الاقتناص ملوكي الحين بدون ذكر أي اسم لشركة ذكاء اصطناعي نهائياً."
    )
    if OPENAI_API_KEY:
        try:
            image_base64 = base64.b64encode(image_bytes).decode('utf-8')
            url = "https://api.openai.com/v1/chat/completions"
            headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
            payload = {
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_base64}"}}]}],
                "temperature": 0.0
            }
            res = requests.post(url, json=payload, headers=headers, timeout=15)
            if res.status_code == 200:
                return f"👑 **SmartEntry Global | وحدة التحليل البصري والمقاصة** 👑\n\n" + res.json()['choices'][0]['message']['content']
        except Exception: pass
    return "❌ خطأ أمني: لتفعيل ميزة المسح بالعين البصرية للشارتات الحية من الجوال، يرجى تزويد السيرفر بمفتاح OPENAI_API_KEY مشحون."
