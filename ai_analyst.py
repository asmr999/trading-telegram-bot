import os
import google.generativeai as genai

# سحب المفتاح السري بأمان من سيرفر ريندر
GOOGLE_API_KEY = os.environ.get("GEMINI_API_KEY")

if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

def analyze_chart_image(image_bytes):
    """تحليل يدوي بالعين البصرية عند إرسال صورة شارت"""
    prompt = (
        "أنت المحلل الفني الخبير وحش الأسواق الملوكية. حلل هذا الشارت المرفق (ذهب، عملات، أو مؤشرات) "
        "وأعطني اتجاه السيولة، ومناطق الدعم والمقاومة الحالية، ونقاط الدخول المقترحة للاستراتيجية بشكل دقيق ومختصر."
    )
    try:
        image_parts = [{"mime_type": "image/png", "data": bytes(image_bytes)}]
        
        # 🎯 تجربة الموديلات البصرية بالترتيب لتخطي عقبة الـ 404 كلياً
        for model_name in ['gemini-pro-vision', 'gemini-1.5-flash', 'gemini-1.5-flash-latest']:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content([prompt, image_parts[0]])
                return response.text
            except Exception:
                continue
        return "❌ خطأ سيرفر جوجل: تعذر العثور على نموذج رؤية متوافق مع إصدار المكتبة الحالي."
    except Exception as e:
        return f"❌ خطأ في معالجة الصورة: {str(e)}"

def analyze_market_data_text(indicators_text):
    """تحليل تلقائي للبيانات الحية الموردة من السيرفر بدون صور"""
    prompt = (
        "أنت المستشار المالي والوحش الخبير in قراءة حركة تدفق السيولة للذهب والعملات العالمية.\n"
        "أمامك تقرير فني حي ومفصل للمؤشرات الفنية الحالية للسوق. ادرس هذه المعطيات الرقمية بدقة، "
        "ثم قم بصياغة صفقة تداول ملوكية متكاملة ومحددة تماماً (اتجاه الصفقة بيع/شراء، سعر الدخول المقترح، الأهداف الحتمية، وقف الخسارة الصارم)، "
        "متبوعاً بشرح عبقري ومختصر لسبب الدخول بناءً على تلك المؤشرات الفنية المرفقة. صغ الرد بأسلوب احترافي ملوكي وقوي جداً باللغة العربية.\n\n"
        f"المعطيات الفنية الحالية للسوق:\n{indicators_text}"
    )
    
    # 🎯 تجربة الموديلات النصية بالترتيب؛ لو رفض الأول يلقط الثاني فوراً بدون كراش
    for model_name in ['gemini-pro', 'gemini-1.5-flash', 'gemini-1.5-flash-latest', 'gemini-1.0-pro']:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            return response.text
        except Exception:
            continue
            
    return "❌ خطأ سيرفر جوجل: تعذر العثور على نموذج نصي متوافق مع إصدار المكتبة الحالي."
