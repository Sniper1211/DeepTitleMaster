from flask import Flask, request, render_template
import sys
import os

# 添加项目根目录到系统路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入主应用，使用不同的变量名避免循环引用
from app import app as flask_app

# 这个文件作为Vercel的入口点
# Vercel Python运行时需要一个名为index的模块，其中包含一个名为app的WSGI应用

# 显式导出app变量，使Vercel能够正确识别并调用Flask应用
app = flask_app

# Vercel Serverless函数入口点
from flask import Response

def handler(request):
    """Vercel Serverless函数入口点
    
    Vercel的Python运行时会调用这个函数处理HTTP请求
    参数:
        request: 包含HTTP请求信息的对象
    
    返回:
        返回Flask应用的响应
    """
    # 直接返回Flask应用实例，让Vercel处理WSGI转换
    return app