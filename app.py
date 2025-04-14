import os
import json
from flask import Flask, request, render_template
from dotenv import load_dotenv
import requests

load_dotenv()
app = Flask(__name__)

# 简易数据库路径
TITLES_DB = os.path.join('database', 'titles.json')
CONFIG_FILE = os.path.join('database', 'config.json')
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')

class TitleGenerator:
    @staticmethod
    def generate(keywords, platform='general'):
        """核心生成逻辑"""
        # 读取模板配置
        with open(CONFIG_FILE, 'r') as f:
            templates = json.load(f).get(platform, {})
        
        # 构建prompt
        prompt = f"""你是一个专业的内容运营专家，请根据以下要求生成5个爆款标题：
        关键词：{keywords}
        平台特性：{templates.get('description', '')}
        必须包含的元素：{templates.get('rules', [])}
        示例格式：{" | ".join(templates.get('examples', []))}
        要求：每个标题不超过20字，使用阿拉伯数字开头"""
        
        # 调用DeepSeek API
        headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}"}
        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers=headers,
            json={
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "max_tokens": 200
            }
        )
        
        # 解析结果
        if response.status_code == 200:
            content = response.json()['choices'][0]['message']['content']
            return [line.strip() for line in content.split('\n') if line.strip()][:5]
        return ["生成失败，请重试"]

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        keywords = request.form['keywords']
        platform = request.form.get('platform', 'general')
        titles = TitleGenerator.generate(keywords, platform)
        return render_template('index.html', titles=titles, keywords=keywords)
    return render_template('index.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    # 简易管理后台
    if request.method == 'POST':
        # 添加新标题
        new_title = request.form['title']
        with open(TITLES_DB, 'r+') as f:
            data = json.load(f)
            data.append({"title": new_title, "status": "active"})
            f.seek(0)
            json.dump(data, f)
    
    with open(TITLES_DB, 'r') as f:
        titles = json.load(f)
    return render_template('admin.html', titles=titles)

if __name__ == '__main__':
    # 初始化数据库文件
    if not os.path.exists(TITLES_DB):
        os.makedirs('database', exist_ok=True)
        with open(TITLES_DB, 'w') as f:
            json.dump([], f)
    
    app.run(debug=True)
