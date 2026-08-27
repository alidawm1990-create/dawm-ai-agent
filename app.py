import os
import base64
import json
import random
import requests
from io import BytesIO
from flask import Flask, jsonify
from google import genai
from PIL import Image, ImageDraw

app = Flask(__name__)

# 🔐 جلب المتغيرات الحساسة بأمان من إعدادات البيئة (Environment Variables) في Render
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
WEBSITE_API_URL = os.environ.get("WEBSITE_API_URL")
SECRET_AUTH_KEY = os.environ.get("SECRET_AUTH_KEY")

# مواضيع إخبارية مقترحة ليختار منها الروبوت عشوائياً في كل مرة
TOPICS_POOL = [
    "مستقبل الذكاء الاصطناعي التوليدي وثورة الروبوتات في عام 2026",
    "تأثير التكنولوجيا الحديثة على التعليم الذكي ووظائف المستقبل",
    "أحدث اكتشافات الفضاء الخارجي ورحلات المريخ المأهولة هذا العام",
    "كيف تساهم الطاقة المتجددة والهيدروجين الأخضر في حماية كوكب الأرض",
    "نصائح ذهبية برمجية للمطورين المبتدئين لتعلم الذكاء الاصطناعي"
]

def generate_article_with_gemini(topic):
    """الاستعانة بجميني لإنشاء المقال بصيغة JSON"""
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
        print(f"Error in Gemini: {str(e)}")
        return None

def create_auto_thumbnail():
    """توليد صورة غلاف للمقال بشكل برمجي متناسق مع لون موقعك"""
    img = Image.new('RGB', (800, 450), color='#1e3c72')
    canvas = ImageDraw.Draw(img)
    canvas.rectangle([(0, 430), (800, 450)], fill='#00d2ff')
    canvas.text((40, 200), "Dawm News AI Content", fill='#ffffff')
    
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

@app.route('/')
def home():
    return jsonify({"status": "Bot is running online successfully!"})

@app.route('/run-bot')
def run_bot():
    """الرابط المخصص لإطلاق الروبوت وجعله ينشر فوراً"""
    topic = random.choice(TOPICS_POOL)
    article = generate_article_with_gemini(topic)
    
    if not article:
        return jsonify({"error": "Failed to generate content from Gemini"}), 500
        
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
        return jsonify({"success": True, "server_response": response.json()})
    except Exception as e:
        return jsonify({"error": f"Failed to push to website: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
