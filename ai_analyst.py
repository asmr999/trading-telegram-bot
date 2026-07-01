import os
import base64
import requests

# سحب المفتاح السري بأمان من خزنة سيرفر ريندر
GOOGLE_API_KEY = os.environ.get("GEMINI_API_KEY")

def analyze_chart_image(image_bytes):
    """تحليل الشارت البصري بطلب HTTP مباشر لتفادي تعارض المكتبات"""
    if not GOOGLE_API_KEY:
        return "❌ خطأ أمني: مفتاح GEMINI_API_KEY غير موجود في إعدادات ريندر السرّية."
    
    prompt = (
        "أنت المحلل الفني الخبير وحش الأسواق الملوكية. حلل هذا الشارت المرفق (ذهب، عملات، أو مؤشرات) "
        "وأعطني اتجاه السيولة، ومناغم الدعم والمقاومة الحالية، ونقاط الدخول المقترحة للاستراتيجية بشكل دقيق ومختصر."
    )
    
    try:
        # تحويل داتا الصورة إلى صيغة Base64 المتوافقة مع سيرفر جوجل مباشرة
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        # رابط جوجل الرسمي والمباشر للموديل
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GOOGLE_API_KEY}"
        
        headers = {'Content-Type': 'application/json'}
        payload = {
            "contents": [{
                "parts": [
                    {"text": prompt},
                    {
                        "inlineData": {
                            "mimeType": "image/png",
                            "data": image_base64
                        }
                    }
                ]
            }]
        }
        
        response = requests.post(url, headers=headers, json=payload)
        response_data = response.json()
        
        if response.status_code == 200:
            return response_data['candidates'][0]['content']['parts'][0]['text']
        else:
            error_msg = response_data.get('error', {}).get('message', 'خطأ غير معروف في خوادم جوجل')
            return f"❌ خطأ سيرفر جوجل المباشر: {error_msg}"
            
    except Exception as e:
        return f"❌ خطأ عام في معالجة الصورة: {str(e)}"

def analyze_market_data_text(indicators_text):
    """تحليل البيانات الرقمية الحية بطلب HTTP مباشر صافي 100%"""
    if not GOOGLE_API_KEY:
        return "❌ خطأ أمني: مفتاح GEMINI_API_KEY غير موجود في إعدادات ريندر السرّية."
        
    prompt = (
        "أنت المستشار المالي والوحش الخبير في قراءة حركة تدفق السيولة للذهب والعملات العالمية.\n"
        "أمامك تقرير فني حي ومفصل للمؤشرات الفنية الحالية للسوق. ادرس هذه المعطيات الرقمية بدقة، "
        "ثم قم بصياغة صفقة تداول ملوكية متكاملة ومحددة تماماً (اتجاه الصفقة بيع/شراء، سعر الدخول المقترح، الأهداف الحتمية، وقف الخسارة الصارم)، "
        "متبوعاً بشرح عبقري ومختصر لسبب الدخول بناءً على تلك المؤشرات الفنية المرفقة. صغ الرد بأسلوب احترافي ملوكي وقوي جداً باللغة العربية.\n\n"
        f"المعطيات الفنية الحالية للسوق:\n{indicators_text}"
    )
    
    try:
        # ضرب السيرفر مباشرة بالموديل المستقر المستضيف
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GOOGLE_API_KEY}"
        
        headers = {'Content-Type': 'application/json'}
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }
        
        response = requests.post(url, headers=headers, json=payload)
        response_data = response.json()
        
        if response.status_code == 200:
            return response_data['candidates'][0]['content']['parts'][0]['text']
        else:
            error_msg = response_data.get('error', {}).get('message', 'خطأ غير معروف في خوادم جوجل')
            return f"❌ خطأ سيرفر جوجل المباشر: {error_msg}"
            
    except Exception as e:
        return f"❌ خطأ عام في معالجة البيانات: {str(e)}"
