import os
import google.generativeai as genai

# 🎯 ضع مفتاح الـ API الحقيقي مالتك من جوجل (الذي يبدأ بـ AIzaSy) بين العلامتين هان فوراً:
GOOGLE_API_KEY = os.environ.get("GEMINI_API_KEY", "ضع_مفتاح_الـ_API_الخاص_بك_هنا_AIzaSy")

genai.configure(api_key=GOOGLE_API_KEY)

def analyze_chart_image(image_bytes):
    """تحليل يدوي بالعين البصرية عند إرسال صورة شارت"""
    prompt = (
        "أنت المحلل الفني الخبير وحش الأسواق الملوكية. حلل هذا شارت المرفق (ذهب، عملات، أو مؤشرات) "
        "وأعطني اتجاه السيولة، ومناطق الدعم والمقاومة الحالية، ونقاط الدخول المقترحة للاستراتيجية بشكل دقيق ومختصر."
    )
    try:
        image_parts = [{"mime_type": "image/png", "data": bytes(image_bytes)}]
        
        for model_name in ['gemini-1.5-flash', 'gemini-1.5-flash-latest']:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content([prompt, image_parts[0]])
                return response.text
            except Exception:
                continue
        return "❌ خطأ: مفتاح الـ API مرفوض من جوجل لمعالجة الصور. تأكد من صلاحية المفتاح."
    except Exception as e:
        return f"❌ خطأ في معالجة داتا الصورة: {str(e)}"

def analyze_market_data_text(indicators_text):
    """تحليل تلقائي موسع للبيانات الحية الموردة من السيرفر بدون صور"""
    prompt = (
        "أنت المستشار المالي والوحش الخبير في قراءة حركة تدفق السيولة للذهب والعملات العالمية.\n"
        "أمامك تقرير فني حي ومفصل للمؤشرات الفنية الحالية للسوق. ادرس هذه المعطيات الرقمية بدقة، "
        "ثم قم بصياغة صفقة تداول ملوكية متكاملة ومحددة تماماً (اتجاه الصفقة بيع/شراء، سعر الدخول المقترح، الأهداف الحتمية، وقف الخسارة الصارم)، "
        "متبوعاً بشرح عبقري ومختصر لسبب الدخول بناءً على تلك المؤشرات الفنية المرفقة. صغ الرد بأسلوب احترافي ملوكي وقوي جداً باللغة العربية.\n\n"
        f"المعطيات الفنية الحالية للسوق:\n{indicators_text}"
    )
    
    # تجربة الموديلات المتاحة غصب عن السيرفر
    for model_name in ['gemini-1.5-flash', 'gemini-1.5-flash-latest', 'gemini-pro']:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            # إذا كان الخطأ بسبب المفتاح، ح يظهر في اللوغات لتسهيل المراقبة
            print(f"Model {model_name} failed: {str(e)}")
            continue
            
    return f"❌ خطأ تفعيل: مفتاح الـ API المستخدم حالياً غير صحيح أو منتهي الصلاحية في حساب Google AI Studio."
