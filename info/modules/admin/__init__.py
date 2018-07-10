from flask import Blueprint

# 创建蓝图对象
from flask import redirect
from flask import request
from flask import session
from flask import url_for

admin_blu = Blueprint('admin',__name__)

# 使用蓝图去注册路由
from . import views


@admin_blu.before_request
def check_admin():
    # 如果不是管理员,那么直接跳转到主页
    is_admin = session.get("is_admin",False)
    # if not is_admin and 当前访问的url不是管理员登入页面
    if not is_admin and not request.url.endswith(url_for("admin.login")):
        return redirect("/")