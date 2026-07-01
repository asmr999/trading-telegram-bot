import os
import google.generativeai as genai

# 🔐 الكود الحين صار يسحب المفتاح بأمان من سيرفر ريندر مباشرة بدون ما ينكشف في جيت هاب
GOOGLE_API_KEY = os.environ.get("GEMINI_API_KEY")

if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
else:
    print("⚠️ تحذير أمني: لم يتم العثور على مفتاح GEMINI_API_KEY في إعدادات السيرفر!")

def analyze_chart_image(image_bytes):
    """تحليل يدوي بالعين البصرية عند إرسال صورة شارت"""
    prompt = (
        "أنت المحلل الفني الخبير وحش الأسواق الملوكية. حلل هذا الشارت المرفق (ذهب، عملات، أو مؤشرات) "
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
        return "❌ خطأ أمني: تعذر الاتصال بالـ AI، يرجى التحقق من متغيرات السيرفر السرية."
    except Exception as e:
        return f"❌ خطأ في معالجة داتا الصورة: {str(e)}"

def analyze_market_data_text(indicators_text):
    """تحليل تلقائي للبيانات الحية الموردة من السيرفر بدون صور"""
    prompt = (
        "أنت المستشار المالي والوحش الخبير في قراءة حركة تدفق السيولة للذهب والعملات العالمية.\n"
        "أمامك تقرير فني حي ومفصل للمؤشرات الفنية الحالية للسوق. ادرس هذه المعطيات الرقمية بدقة، "
        "ثم قم بصياغة صفقة تداول ملوكية متكاملة ومحددة تماماً (اتجاه الصفقة بيع/شراء، سعر الدخول المقترح، الأهداف الحتمية، وقف الخسارة الصارم)، "
        "متبوعاً بشرح عبقري ومختصر لسبب الدخول بناءً على تلك المؤشرات الفنية المرفقة. صغ الرد بأسلوب احترافي ملوكي وقوي جداً باللغة العربية.\n\n"
        f"المعطيات الفنية الحالية للسوق:\n{indicators_text}"
    )
    for model_name in ['gemini-1.5-flash', 'gemini-1.5-flash-latest', 'gemini-pro']:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            return response.text
        except Exception:
            continue
    return "❌ خطأ تفعيل: تعذر قراءة البيانات الفنية الرقمية، تأكد من إعدادات المفتاح السري في ريندر."
