import os
import base64
import json
import random
import requests
import threading  # 🧵 ميزة العمل الخلفي لحل مشكلة توقف السيرفر المجاني
from io import BytesIO
from flask import Flask, jsonify
from google import genai
from PIL import Image, ImageDraw

app = Flask(__name__)

# جلب المتغيرات السرية بأمان من Render
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
WEBSITE_API_URL = os.environ.get("WEBSITE_API_URL")
SECRET_AUTH_KEY = os.environ.get("SECRET_AUTH_KEY")

TOPICS_POOL = [
    "مستقبل الذكاء الاصطناعي التوليدي وثورة الروبوتات في عام 2026",
    "تأثير التكنولوجيا الحديثة على التعليم الذكي ووظائف المستقبل",
    "أحدث اكتشافات الفضاء الخارجي ورحلات المريخ المأهولة هذا العام",
    "كيف تساهم الطاقة المتجددة والهيدروجين الأخضر في حماية كوكب الأرض",
    "نصائح ذهبية برمجية للمطورين المبتدئين لتعلم الذكاء الاصطناعي"
]

def generate_article_with_gemini(topic):
    """الاتصال بجميني لجلب المقال"""
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        prompt = f"""
        اكتب مقالاً إخبارياً احترافياً ومفصلاً باللغة العربية عن الموضوع التالي: {topic}.
        يجب أن تكون الإجابة بصيغة JSON نظيفة جداً وبدون أي علامات اقتباس برمجية مثل ```json.
        استخدم الهيكل التالي للـ JSON:
        {{
            "title": "عنوان المقال الجذاب هنا",
            "content": "موضوع ونص المقال بالكامل هنا بشكل منسق ومفصل جداً",
            "tags": "كلمات، مفتاحية، مقسمة، بفاصلة"
        }}
        """
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        text_data = response.text.strip().replace("```json", "").replace("```", "")
        return json.loads(text_data)
    except Exception as e:
        print(f"❌ خطأ أثناء الاتصال بجميني: {str(e)}")
        return None

def create_auto_thumbnail():
    """توليد صورة الغلاف برمجياً وبسرعة فائقة"""
    try:
        img = Image.new('RGB', (800, 450), color='#1e3c72')
        canvas = ImageDraw.Draw(img)
        canvas.rectangle([(0, 430), (800, 450)], fill='#00d2ff')
        
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode('utf-8')
    except Exception as e:
        print(f"❌ خطأ أثناء رسم الصورة: {str(e)}")
        return None

def async_bot_task(topic):
    """هذه الدالة تعمل بالكامل خلف الكواليس لحماية السيرفر المجاني من التوقف"""
    print(f"🤖 بدأ الروبوت العمل على موضوع: {topic}")
    article = generate_article_with_gemini(topic)
    
    if not article:
        print("❌ توقف العمل: لم يتم استقبال بيانات من جميني.")
        return
        
    image_b64 = create_auto_thumbnail()
    
    payload = {
        "title": article['title'],
        "content": article['content'],
        "tags": article['tags'],
        "lang": "ar",
        "image_base64": image_b64
    }
    
    headers = {
        "Authorization": SECRET_AUTH_KEY,
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(WEBSITE_API_URL, json=payload, headers=headers)
        print(f"🎉 تم إنهاء العملية وضخ المقال بنجاح! رد الموقع الإخباري: {response.text}")
    except Exception as e:
        print(f"❌ خطأ أثناء ضخ المقال للموقع: {str(e)}")

@app.route('/')
def home():
    return jsonify({"status": "Bot is running online successfully!"})

@app.route('/run-bot')
def run_bot():
    """الرابط يستجيب فوراً في جزء من الثانية لمتصفحك، ويترك الروبوت يعمل بالخلفية بأمان"""
    topic = random.choice(TOPICS_POOL)
    
    # 🧵 إطلاق خيط معالجة خلفي مستقل
    thread = threading.Thread(target=async_bot_task, args=(topic,))
    thread.start()
    
    return jsonify({
        "success": True, 
        "message": "🤖 تم إيقاظ الوكيل الذكي بنجاح! جاري توليد المقال ورسم الصورة ونشرها خلف الكواليس حالياً."
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
