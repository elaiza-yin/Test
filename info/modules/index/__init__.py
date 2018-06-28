from flask import Blueprint

# 创建蓝图对象
index_blu = Blueprint('index',__name__)

# 使用蓝图去注册路由
from . import views