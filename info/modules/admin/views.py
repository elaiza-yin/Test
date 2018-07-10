from flask import current_app
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for

from info.models import User
from info.modules.admin import admin_blu


@admin_blu.route("/index")
def index():
    return render_template("admin/index.html")


@admin_blu.route("/login",methods=["GET","POST"])
def login():
    # : 为GET请求时
    if request.method == "GET":
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