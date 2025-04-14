from flask import Flask, request, render_template
import sys
import os

# 添加项目根目录到系统路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入主应用
from app import app

# 这个文件作为Vercel的入口点
# Vercel Python运行时需要一个名为index的模块，其中包含一个名为app的WSGI应用

# 显式导出app变量，使Vercel能够正确识别并调用Flask应用
app = app