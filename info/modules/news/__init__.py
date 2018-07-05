from flask import Blueprint

# 创建蓝图对象
news_blu = Blueprint('news',__name__,url_prefix='/news')

# 使用蓝图去注册路由
from . import views