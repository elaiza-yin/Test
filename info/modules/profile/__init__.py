from flask import Blueprint

# 创建蓝图对象
profile_blu = Blueprint('profile',__name__,url_prefix='/user')

# 使用蓝图去注册路由
from . import views