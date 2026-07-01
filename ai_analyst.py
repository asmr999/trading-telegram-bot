import os
import google.generativeai as genai

# إعداد مفتاح الـ API الخاص بجوجل من السيرفر
GOOGLE_API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyD-YOUR-ACTUAL-KEY")
genai.configure(api_key=GOOGLE_API_KEY)

def analyze_chart_image(image_bytes):
    try:
        # تحضير داتا الصورة بشكل متوافق مع بايثون
        image_parts = [
            {
                "mime_type": "image/png",
                "data": bytes(image_bytes)
            }
        ]
        
        # 🎯 استخدام الاسم الصافي والمعتمد لتجنب خطأ الـ 404 كلياً
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = (
            "أنت المحلل الفني الخبير وحش الأسواق الملوكية. حلل هذا الشارت المرفق (ذهب، عملات، أو مؤشرات) "
            "وأعطني اتجاه السيولة، ومناطق الدعم والمقاومة الحالية، ونقاط الدخول المقترحة للاستراتيجية بشكل دقيق ومختصر."
        )
        
        response = model.generate_content([prompt, image_parts[0]])
        return response.text
        
    except Exception as e:
        # محاولة بديلة باسم الموديل المحدث في حال اختلاف نسخة المكتبة
        try:
            model = genai.GenerativeModel('gemini-1.5-flash-latest')
            response = model.generate_content([prompt, image_parts[0]])
            return response.text
        except Exception as inner_e:
            return f"❌ خطأ في الاتصال بالذكاء الاصطناعي: {str(inner_e)}"
