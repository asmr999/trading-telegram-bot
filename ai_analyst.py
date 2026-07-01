import os
import base64
import requests

# سحب المفاتيح السرية الحصينة من إعدادات ريندر
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# 🎯 الأمر العسكري الصارم لضمان دقة الصفقة وإدارة المخاطر الحتمية
SYSTEM_PROMPT = (
    "أنت المستشار المالي وكبير المحللين الفنيين في غرف التداول العالمية للذهب والعملات.\n"
    "أمامك تقرير فني حي ومفصل للمؤشرات الفنية الحالية للسوق. ادرس المعطيات الرياضية بحذر شديد، "
    "ثم قم بصياغة صفقة تداول ملوكية متكاملة ومحددة تماماً بناءً على القواعد التالية:\n"
    "1. يجب أن تشتمل الصفقة على: (اتجاه الصفقة بيع/شراء، سعر الدخول المقترح، 3 أهداف حتمية، وقف خسارة صارم).\n"
    "2. يُمنع منعاً باتاً صياغة أي صفقة ما لم يكن معدل الربح إلى الخسارة (Risk:Reward Ratio) يساوي 1:2 على الأقل.\n"
    "3. إذا كانت المؤشرات الفنية متضاربة، أو السيولة ضعيفة، أو السوق غير واضح، اكتب فوراً العبارة التالية في بداية الرد: "
    "⚠️ [تنبيه الليدر]: المؤشرات الحالية متضاربة وغير آمنة، نفضل الانتظار خارج الشاشات الحين لحماية رأس المال.\n"
    "صغ الرد بأسلوب احترافي ملوكي وقوي جداً باللغة العربية، واجعل تحليلك جافاً ورياضياً 100%."
)

def analyze_market_data_text(indicators_text):
    """تحليل المعطيات الرقمية بأعلى دقة ونسبة ذكاء صفرية لمنع التخريف"""
    full_prompt = f"{SYSTEM_PROMPT}\n\nالمعطيات الفنية الحالية للسوق:\n{indicators_text}"

    # 1️⃣ خط الدفاع الأول: وحش السرعة الخارق Groq (Llama 3)
    if GROQ_API_KEY:
        try:
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
            payload = {
                "model": "llama3-70b-8192",
                "messages": [{"role": "user", "content": full_prompt}],
                "temperature": 0.0  # تفعيل المنطق الرياضي الصارم
            }
            res = requests.post(url, json=payload, headers=headers, timeout=10)
            if res.status_code == 200:
                return "🎯 [تحليل Groq الرياضي]:\n" + res.json()['choices'][0]['message']['content']
        except Exception:
            pass

    # 2️⃣ خط الدفاع الثاني: الجوكر المجاني العبقري OpenRouter (DeepSeek / Llama 3)
    if OPENROUTER_API_KEY:
        try:
            url = "https://openrouter.ai/api/v1/chat/completions"
            headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}
            payload = {
                "model": "meta-llama/llama-3-70b-instruct:free",
                "messages": [{"role": "user", "content": full_prompt}],
                "temperature": 0.0
            }
            res = requests.post(url, json=payload, headers=headers, timeout=10)
            if res.status_code == 200:
                return "🌐 [تحليل OpenRouter المجاني]:\n" + res.json()['choices'][0]['message']['content']
        except Exception:
            pass

    # 3️⃣ خط الدفاع الثالث: العقل المستقر والشهير OpenAI (GPT-4o-mini)
    if OPENAI_API_KEY:
        try:
            url = "https://api.openai.com/v1/chat/completions"
            headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
            payload = {
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": full_prompt}],
                "temperature": 0.0
            }
            res = requests.post(url, json=payload, headers=headers, timeout=10)
            if res.status_code == 200:
                return "🦅 [تحليل OpenAI المحترف]:\n" + res.json()['choices'][0]['message']['content']
        except Exception:
            pass

    # 4️⃣ خط الدفاع الأخير: العودة المباشرة لجوجل جيميناي
    if GEMINI_API_KEY:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
            payload = {
                "contents": [{"parts": [{"text": full_prompt}]}],
                "generationConfig": {"temperature": 0.0}
            }
            res = requests.post(url, json=payload, headers={'Content-Type': 'application/json'}, timeout=10)
            if res.status_code == 200:
                return "🤖 [تحليل Gemini الاحتياطي]:\n" + res.json()['candidates'][0]['content']['parts'][0]['text']
        except Exception:
            pass

    return "❌ عذراً يا ليدر: جميع خوادم الذكاء الاصطناعي (Groq, OpenRouter, OpenAI, Gemini) لم تستجب أو تحتاج لتفعيل مفاتيحها السرية في ريندر."

def analyze_chart_image(image_bytes):
    """تحليل صور الشارتات بالعين البصرية بالاعتماد على OpenAI أو OpenRouter لضمان دقة الرؤية"""
    prompt = (
        "أنت كبار المحللين الفنيين. حلل شارت الذهب/العملات المرفق بدقة رياضية، "
        "واستخرج الاتجاه الفعلي للسيولة، ومناطق الدعم والمقاومة، ونقاط اقتناص الصفقات الفورية ملوكي."
    )
    
    # الاعتماد الأساسي للصور على OpenAI لقوتها الفائقة
    if OPENAI_API_KEY:
        try:
            image_base64 = base64.b64encode(image_bytes).decode('utf-8')
            url = "https://api.openai.com/v1/chat/completions"
            headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
            payload = {
                "model": "gpt-4o-mini",
                "messages": [{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_base64}"}}
                    ]
                }],
                "temperature": 0.0
            }
            res = requests.post(url, json=payload, headers=headers, timeout=15)
            if res.status_code == 200:
                return "🦅 [تحليل العين البصرية - OpenAI]:\n" + res.json()['choices'][0]['message']['content']
        except Exception as e:
            return f"❌ خطأ OpenAI البصري: {str(e)}"
            
    return "❌ خطأ رؤية: لتفعيل الفحص بالعين البصرية للشارتات، يرجى تزويد السيرفر بمفتاح OPENAI_API_KEY مشحون."
