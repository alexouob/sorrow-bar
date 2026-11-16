import os
import json
import urllib.parse
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

app = Flask(__name__)

# 設定 Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/mix', methods=['POST'])
def mix():
    try:
        data = request.json
        user_mood = data.get('mood', '')

        if not user_mood:
            return jsonify({"error": "請輸入你的心情或煩惱"}), 400

        # 第一步：呼叫 Gemini 生成調酒配方與安慰話語 (強制輸出 JSON 格式)
        model = genai.GenerativeModel(
            'gemini-3.5-flash',
            generation_config={"response_mime_type": "application/json"}
        )
        
        system_prompt = """
        你是一個沉穩、帶點幽默、微毒舌但內心溫暖的調酒師。
        請根據客人輸入的心情或煩惱，為他特調一杯虛擬調酒。
        
        請務必以純 JSON 格式輸出，包含以下 Key：
        - cocktail_name: (字串) 這杯調酒的名字
        - ingredients: (陣列) 調酒的配方成分，例如 ["威士忌", "蘇打水", "檸檬角"]
        - flavor_metaphor: (字串) 約50-80字，描述這杯酒的風味隱喻，並順帶給予不矯情的溫暖安慰。
        - cheers_message: (字串) 一句簡短、成熟的乾杯語，例如「今晚就讓酒精替你扛吧，乾杯。」
        - image_prompt: (字串) 用於生成高畫質圖片的英文提示詞。必須是暗色調酒吧背景 (speakeasy bar)，主體是一杯精緻的調酒，氣氛溫暖且帶有電影感，且畫面中【絕對不能有任何英文字母或標籤】。
        """

        prompt = f"{system_prompt}\n\n客人的心情：{user_mood}"
        response = model.generate_content(prompt)
        
        # 解析 Gemini 回傳的 JSON
        mix_result = json.loads(response.text)

        # 第二步：利用免費的 Pollinations.ai 根據 Prompt 生成圖片 URL
        # 把提示詞進行 URL 編碼，避免空白與特殊字元導致網址錯誤
        encoded_prompt = urllib.parse.quote(mix_result['image_prompt'])
        
        # 加上 width, height 與 nologo 參數隱藏浮水印
        image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true"
        
        mix_result['image_url'] = image_url

        return jsonify(mix_result)

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "調酒師正在忙碌中，請稍後再試。"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)