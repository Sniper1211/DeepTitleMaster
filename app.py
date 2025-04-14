import os
import json
from flask import Flask, request, render_template
from dotenv import load_dotenv
import requests

app = Flask(__name__)

# 简易数据库路径
TITLES_DB = os.path.join(os.path.dirname(__file__), 'database', 'titles.json')
CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'database', 'config.json')
DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY')
DEEPSEEK_API_URL = os.environ.get('DEEPSEEK_API_URL')

class TitleGenerator:
    @staticmethod
    def generate(keywords, platform='general'):
        """核心生成逻辑"""
        try:
            # 读取模板配置
            with open(CONFIG_FILE, 'r') as f:
                templates = json.load(f).get(platform, {})
        except (IOError, json.JSONDecodeError) as e:
            print(f"配置文件读取错误: {str(e)}")
            templates = {
                "description": "通用平台",
                "rules": ["数字开头", "20字以内"],
                "examples": ["1个月瘦20斤，这样吃就对了", "3招教你月入过万"]
            }
        
        # 构建prompt
        prompt = f"""你是一个专业的内容运营专家，请根据以下要求生成5个爆款标题：
        关键词：{keywords}
        平台特性：{templates.get('description', '')}
        必须包含的元素：{templates.get('rules', [])}
        示例格式：{" | ".join(templates.get('examples', []))}
        要求：每个标题不超过20字，使用阿拉伯数字开头"""
        
        # 调用DeepSeek API
        headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}"}
        api_url = DEEPSEEK_API_URL
        
        try:
            response = requests.post(
                api_url,
                headers=headers,
                json={
                    "model": "deepseek-chat",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7,
                    "max_tokens": 200
                },
                timeout=30
            )
            
            # 解析结果
            if response.status_code == 200:
                content = response.json()['choices'][0]['message']['content']
                return [line.strip() for line in content.split('\n') if line.strip()][:5]
            else:
                print(f"API错误: {response.status_code} - {response.text}")
                return [f"生成失败，API返回错误: {response.status_code}"]
        except Exception as e:
            print(f"API调用异常: {str(e)}")
            return [f"生成失败: {str(e)}"]

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
        action = request.form.get('action', 'add')
        
        if action == 'add':
            # 添加新标题
            new_title = request.form.get('title')
            if new_title:
                with open(TITLES_DB, 'r+') as f:
                    data = json.load(f)
                    data.append({"title": new_title, "status": "active"})
                    f.seek(0)
                    f.truncate()
                    json.dump(data, f)
        
        elif action == 'edit':
            # 编辑标题
            title_id = int(request.form.get('title_id'))
            new_title = request.form.get('new_title')
            new_status = request.form.get('status')
            
            with open(TITLES_DB, 'r+') as f:
                data = json.load(f)
                if 0 <= title_id < len(data):
                    if new_title:
                        data[title_id]['title'] = new_title
                    if new_status:
                        data[title_id]['status'] = new_status
                    f.seek(0)
                    f.truncate()
                    json.dump(data, f)
        
        elif action == 'delete':
            # 删除标题
            title_id = int(request.form.get('title_id'))
            with open(TITLES_DB, 'r+') as f:
                data = json.load(f)
                if 0 <= title_id < len(data):
                    del data[title_id]
                    f.seek(0)
                    f.truncate()
                    json.dump(data, f)
    
    with open(TITLES_DB, 'r') as f:
        titles = json.load(f)
    return render_template('admin.html', titles=titles)

if __name__ == '__main__':
    app.run(debug=True)

def init_database():
    """初始化数据库文件"""
    db_dir = os.path.join(os.path.dirname(__file__), 'database')
    os.makedirs(db_dir, exist_ok=True)
    if not os.path.exists(TITLES_DB):
        with open(TITLES_DB, 'w') as f:
            json.dump([], f)
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'w') as f:
            json.dump({
                "general": {
                    "description": "通用平台",
                    "rules": ["数字开头", "20字以内"],
                    "examples": ["1个月瘦20斤，这样吃就对了", "3招教你月入过万"]
                }
            }, f)

# 在应用启动时初始化数据库
init_database()

# Vercel需要的入口函数
def handler(event, context):
    """Vercel Serverless函数入口点"""
    init_database()  # 确保在Vercel环境中也初始化数据库
    return app.wsgi_app
