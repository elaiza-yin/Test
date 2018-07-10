from flask import current_app
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for

from info.models import User
from info.modules.admin import admin_blu
from info.utils.common import user_login_data


@admin_blu.route("/index")
@user_login_data
def index():
    user = g.user
    return render_template("admin/index.html" , data = user.to_dict())


@admin_blu.route("/login",methods=["GET","POST"])
def login():
    # : 为GET请求时
    if request.method == "GET":
        # 判断当前是否有登入,如果有登入就直接重定向到后台管理页面
        user_id = session.get("user_id",None)
        is_admin = session.get("is_admin",None)
        if user_id and is_admin:
            return redirect(url_for("admin.index"))
        return render_template("admin/login.html")

    # : 为POST请求时,前端会使用form表单的提交
    username = request.form.get("username")
    password = request.form.get("password")

    # : 判断参数
    if not all([username,password]):
        return render_template("admin/login.html" , errmsg="参数有误")

    # : 查询当前用户
    try:
        user = User.query.filter(User.mobile==username,User.is_admin==True).first()
    except Exception as e:
        current_app.logger.error(e)
        return render_template("admin/login.html", errmsg="用户信息查询失败")
    if not user:
        return render_template("admin/login.html", errmsg="未查询到用户的信息")

    # : 校验密码
    if not user.check_passowrd(password):
        return render_template("admin/login.html", errmsg="管理员密码错误")

    # : 保存用户的登入信息
    session["user_id"] = user.id
    session["mobile"] = user.mobile
    session["nick_name"] = user.nick_name
    session["is_admin"] = True

    # : 跳转到后台管理页面admin文件夹下的index.html(重定向)
    return redirect(url_for("admin.index"))