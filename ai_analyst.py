import os
import base64
import requests

# 🔐 خزنة المفاتيح الحرة
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
SAMBANOVA_API_KEY = os.environ.get("SAMBANOVA_API_KEY")
COHERE_API_KEY = os.environ.get("COHERE_API_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY") # العين المجانية المستقرة من Google AI Studio

# 🎭 الميثاق المؤسسي الصارم لحجب الهوية
INSTITUTIONAL_PROMPT = (
    "أنت رئيس اللجنة الفنية العليا لإدارة المخاطر بصندوق SmartEntry الاستثماري العالمي.\n"
    "يُمنع منعاً باتاً ذكر أنك ذكاء اصطناعي أو الإشارة لأسماء شركات التكنولوجيا نهائياً.\n"
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
    """👁️ العين البصرية الإنتاجية: قراءة شارتات الآيفون بالمسار الصافي v1 لحرق خطأ 404 كلياً للأبد"""
    if not GEMINI_API_KEY:
        return "❌ خطأ سيرفر: يرجى تزويد ريندر بمفتاح `GEMINI_API_KEY` المجاني لتفعيل العين البصرية للشارتات الحين."
        
    try:
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        # 🔥 الإغلاق الصارم: الانتقال إلى رابط الإنتاج الرسمي المستقر v1 وحذف كلمة beta تماماً
        url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        
        vision_prompt = (
            "You are the Head of Technical Analysis at SmartEntry Global Fund. Look carefully at this screenshot image of a financial chart from the user's mobile.\n"
            "Analyze the candlestick pattern, the support/resistance zones, and the current exact market price visible on the right axis.\n"
            "Formulate a highly accurate trading signal in Arabic with 100% human-like professional tone. Do not mention Gemini, AI, or any tech company. Provide:\n"
            "1. Market Direction (BUY / SELL / WAIT)\n"
            "2. Exact Entry Point, 3 Take-Profit Targets, and a tight Stop-Loss matching 1:2 risk/reward ratio.\n"
            "3. Visual structural justification from the candles."
        )
        
        payload = {
            "contents": [{
                "parts": [
                    {"text": vision_prompt},
                    {"inline_data": {"mime_type": "image/jpeg", "data": image_base64}}
                ]
            }],
            "generation_config": {"temperature": 0.0}
        }
        
        res = requests.post(url, json=payload, headers={'Content-Type': 'application/json'}, timeout=15)
        if res.status_code == 200:
            res_json = res.json()
            if 'candidates' in res_json and len(res_json['candidates']) > 0:
                report = res_json['candidates'][0]['content']['parts'][0]['text']
                return f"👑 **SmartEntry Global | وحدة التحليل البصري الحية والذكية** 👑\n\n" + report
            else:
                return f"❌ خطأ: استجابة خادم الرؤية فارغة، يرجى إعادة التقاط الصورة وإرسالها الحين."
        else:
            # 🛡️ حقن نظام كاشف الأعطال الفوري: طباعة نص رد جوجل الحقيقي لمنع التخمين نهائياً
            return f"❌ **خطأ في خادم الرؤية المباشر (كود {res.status_code}):**\n`{res.text[:140]}`\n\n💡 *إجراء فوري الحين:* تأكد من سلامة وصحة المفتاح المضاف في ريندر."
            
    except Exception as e:
        return f"❌ خطأ فني أثناء مسح الشارت البصري الحين: {str(e)[:100]}"
