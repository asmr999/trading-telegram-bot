import os
import base64
import requests

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

SYSTEM_PROMPT = "أنت مستشار مالي فني، حلل هذه المؤشرات بدقة وأعطني صفقة تداول واضحة."

def analyze_market_data_text(indicators_text):
    full_prompt = f"{SYSTEM_PROMPT}\n\nالمعطيات:\n{indicators_text}"
    report = ["🔍 **تقرير الفحص التشخيصي للمحركات الحية:**"]

    # 1️⃣ فحص جروك
    if GROQ_API_KEY:
        try:
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
            payload = {"model": "llama3-70b-8192", "messages": [{"role": "user", "content": full_prompt}], "temperature": 0.0}
            res = requests.post(url, json=payload, headers=headers, timeout=10)
            if res.status_code == 200:
                return res.json()['choices'][0]['message']['content']
            else:
                report.append(f"❌ Groq (موجود ولكن السيرفر رفض): {res.status_code} - {res.text[:100]}")
        except Exception as e:
            report.append(f"❌ Groq (خطأ اتصال): {str(e)}")
    else:
        report.append("⚪ Groq: غير مفعّل (المفتاح مفقود في ريندر)")

    # 2️⃣ فحص أوبن روتر
    if OPENROUTER_API_KEY:
        try:
            url = "https://openrouter.ai/api/v1/chat/completions"
            headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}
            payload = {"model": "meta-llama/llama-3-70b-instruct:free", "messages": [{"role": "user", "content": full_prompt}], "temperature": 0.0}
            res = requests.post(url, json=payload, headers=headers, timeout=10)
            if res.status_code == 200:
                return res.json()['choices'][0]['message']['content']
            else:
                report.append(f"❌ OpenRouter (موجود ولكن رفض): {res.status_code} - {res.text[:100]}")
        except Exception as e:
            report.append(f"❌ OpenRouter (خطأ اتصال): {str(e)}")
    else:
        report.append("⚪ OpenRouter: غير مفعّل (المفتاح مفقود في ريندر)")

    # 3️⃣ فحص أوبن إيه آي
    if OPENAI_API_KEY:
        try:
            url = "https://api.openai.com/v1/chat/completions"
            headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
            payload = {"model": "gpt-4o-mini", "messages": [{"role": "user", "content": full_prompt}], "temperature": 0.0}
            res = requests.post(url, json=payload, headers=headers, timeout=10)
            if res.status_code == 200:
                return res.json()['choices'][0]['message']['content']
            else:
                report.append(f"❌ OpenAI (موجود ولكن رفض): {res.status_code} - {res.json().get('error', {}).get('message', '')}")
        except Exception as e:
            report.append(f"❌ OpenAI (خطأ اتصال): {str(e)}")
    else:
        report.append("⚪ OpenAI: غير مفعّل (المفتاح مفقود في ريندر)")

    # 4️⃣ فحص جيمناي المباشر
    if GEMINI_API_KEY:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
            payload = {"contents": [{"parts": [{"text": full_prompt}]}], "generationConfig": {"temperature": 0.0}}
            res = requests.post(url, json=payload, headers={'Content-Type': 'application/json'}, timeout=10)
            if res.status_code == 200:
                return res.json()['candidates'][0]['content']['parts'][0]['text']
            else:
                report.append(f"❌ Gemini (موجود ولكن رفض): {res.status_code} - {res.json().get('error', {}).get('message', '')}")
        except Exception as e:
            report.append(f"❌ Gemini (خطأ اتصال): {str(e)}")
    else:
        report.append("⚪ Gemini: غير مفعّل (المفتاح مفقود في ريندر)")

    return "\n".join(report)

def analyze_chart_image(image_bytes):
    # يبقى كما هو للصور
    if OPENAI_API_KEY:
        try:
            image_base64 = base64.b64encode(image_bytes).decode('utf-8')
            url = "https://api.openai.com/v1/chat/completions"
            headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
            payload = {"model": "gpt-4o-mini", "messages": [{"role": "user", "content": [{"type": "text", "text": "حلل الشارت"}, {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_base64}"}}]}], "temperature": 0.0}
            res = requests.post(url, json=payload, headers=headers, timeout=15)
            if res.status_code == 200:
                return res.json()['choices'][0]['message']['content']
        except Exception: pass
    return "❌ خطأ رؤية: لتفعيل الفحص بالعين البصرية للشارتات، يرجى تزويد السيرفر بمفتاح OPENAI_API_KEY مشحون."
