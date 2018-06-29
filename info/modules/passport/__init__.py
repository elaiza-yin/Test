# 登入注册的相关逻辑代码都放在当前模块中
from flask import Blueprint

# 创建蓝图对象
passport_blu = Blueprint('passport',__name__ , url_prefix='/passport')

# 使用蓝图去注册路由
from . import views