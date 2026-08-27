import os
import base64
import json
import random
import requests
import threading
from io import BytesIO
from flask import Flask, jsonify
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
    """الاتصال المباشر بـ Gemini عبر الـ API الرسمي بدون مكتبات خارجية"""
    try:
        # رابط الاتصال المباشر بنظام جميني المستقر
        url = f"https://googleapis.com{GEMINI_API_KEY}"
        
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
        
        payload = {
            "contents": [{"parts": [{"text": prompt}]}]
        }
        headers = {"Content-Type": "application/json"}
        
        response = requests.post(url, json=payload, headers=headers)
        response_data = response.json()
        
        # استخراج النص المولد وتنظيفه
        raw_text = response_data['candidates'][0]['content']['parts'][0]['text']
        clean_text = raw_text.strip().replace("```json", "").replace("```", "")
        
        return json.loads(clean_text)
    except Exception as e:
        print(f"❌ خطأ الاتصال بجميني: {str(e)}")
        return None

def create_auto_thumbnail():
    """توليد صورة غلاف للمقال بشكل برمجي فوري"""
    try:
        img = Image.new('RGB', (800, 450), color='#1e3c72')
        canvas = ImageDraw.Draw(img)
        canvas.rectangle([(0, 430), (800, 450)], fill='#00d2ff')
        
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode('utf-8')
    except Exception as e:
        print(f"❌ خطأ رسم الصورة: {str(e)}")
        return None

def async_bot_task(topic):
    """تنفيذ المهمة في الخلفية لضمان استقرار السيرفر"""
    print(f"🤖 جاري العمل على موضوع: {topic}")
    article = generate_article_with_gemini(topic)
    
    if not article:
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
        res = requests.post(WEBSITE_API_URL, json=payload, headers=headers)
        print(f"🎉 تم النشر بنجاح! رد موقعك: {res.text}")
    except Exception as e:
        print(f"❌ خطأ أثناء الضخ للموقع: {str(e)}")

@app.route('/')
def home():
    return jsonify({"status": "Bot is running online successfully!"})

@app.route('/run-bot')
def run_bot():
    topic = random.choice(TOPICS_POOL)
    thread = threading.Thread(target=async_bot_task, args=(topic,))
    thread.start()
    return jsonify({
        "success": True, 
        "message": "🤖 تم إيقاظ الوكيل الذكي بنجاح! جاري توليد المقال ونشره حالياً بالخلفية."
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
