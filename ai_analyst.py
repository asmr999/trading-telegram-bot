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
    errors = []
    try:
        image_parts = [{"mime_type": "image/png", "data": bytes(image_bytes)}]
        for model_name in ['gemini-1.5-flash', 'gemini-pro-vision']:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content([prompt, image_parts[0]])
                return response.text
            except Exception as e:
                errors.append(f"{model_name}: {str(e)}")
                continue
        return f"❌ أخطاء صور جوجل:\n" + "\n".join(errors)
    except Exception as e:
        return f"❌ خطأ عام في معالجة الصورة: {str(e)}"

def analyze_market_data_text(indicators_text):
    """تحليل تلقائي للبيانات الحية الموردة من السيرفر بدون صور"""
    prompt = (
        "أنت المستشار المالي والوحش الخبير في قراءة حركة تدفق السيولة للذهب والعملات العالمية.\n"
        "أمامك تقرير فني حي ومفصل للمؤشرات الفنية الحالية للسوق. ادرس هذه المعطيات الرقمية بدقة، "
        "ثم قم بصياغة صفقة تداول ملوكية متكاملة ومحددة تماماً (اتجاه الصفقة بيع/شراء، سعر الدخول المقترح، الأهداف الحتمية، وقف الخسارة الصارم)، "
        "متبوعاً بشرح عبقري ومختصر لسبب الدخول بناءً على تلك المؤشرات الفنية المرفقة. صغ الرد بأسلوب احترافي ملوكي وقوي جداً باللغة العربية.\n\n"
        f"المعطيات الفنية الحالية للسوق:\n{indicators_text}"
    )
    
    errors = []
    # 🎯 نجمع الأخطاء الحقيقية لكل الموديلات عشان نقفش العلة فوراً على الشات
    for model_name in ['gemini-1.5-flash', 'gemini-pro', 'models/gemini-1.5-flash']:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            errors.append(f"- {model_name} -> {str(e)}")
            continue
            
    return f"❌ تقرير أخطاء سيرفر جوجل الصريح حالياً:\n" + "\n".join(errors)
