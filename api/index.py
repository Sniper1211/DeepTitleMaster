from flask import Flask, request, render_template
import sys
import os

# 添加项目根目录到系统路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入主应用
from app import app

# Vercel Serverless函数入口
def handler(request, response):
    return app(request, response)