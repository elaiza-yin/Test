from flask import current_app, jsonify
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import session

from info import constants
from info import db
from info.modules.profile import profile_blu
from info.utils.common import user_login_data
from info.utils.image_storage import storage
from info.utils.response_code import RET


@profile_blu.route("/pass_info",methods=["GET","POST"])
@user_login_data
def pass_info():
    """个人中心的用户密码修改"""
    # 请求为GET时:展示"密码设置"的界面(渲染模板,不用传递参数)
    if request.method == "GET":
        return render_template("news/user_pass_info.html" )

    # 1. 获取到传入参数
    data_dict = request.json
    old_password = data_dict.get("old_password")
    new_password = data_dict.get("new_password")

    if not all([old_password, new_password]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数有误")

    # 2. 获取当前登录用户的信息
    user = g.user

    if not user.check_passowrd(old_password):
        return jsonify(errno=RET.PWDERR, errmsg="原密码错误")

    # 3. 更新数据
    user.password = new_password
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="保存数据失败")

    return jsonify(errno=RET.OK, errmsg="保存成功")


@profile_blu.route("/pic_info",methods=["GET","POST"])
@user_login_data
def pic_info():
    """个人中心的头像设置[GET 和 POST]"""
    user = g.user

    # 请求为GET时:展示"头像设置"的界面(渲染模板)
    if request.method == "GET":
        data = {
            "user":user.to_dict()
        }
        return render_template("news/user_pic_info.html",data=data)

    # 请求为POST时:就是修改数据
    # 1. 获取到上传的文件
    try:
        avatar_file = request.files.get("avatar").read()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="读取文件出错")

    # 2. 再将文件上传到七牛云
    try:
        url = storage(avatar_file)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg="上传图片错误")

    # 3. 将头像信息更新到当前用户的模型中

    # 设置用户模型相关数据(url图片的key)
    user.avatar_url = url
    # 将数据保存到数据库
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="保存用户数据错误")

    # 4. 返回上传的结果<avatar_url>
    return jsonify(errno=RET.OK, errmsg="OK", data={"avatar_url": constants.QINIU_DOMIN_PREFIX + url})


@profile_blu.route("/base_info",methods=["GET","POST"])
@user_login_data
def base_info():
    """个人中心的基本资料[GET 和 POST]"""
    user = g.user

    # 请求为GET时:展示"基本资料"的界面(渲染模板)
    if request.method == "GET":
        data = {
            "user" : user.to_dict()
        }
        return render_template('news/user_base_info.html',data = data)

    # 请求为POST时:修改用"基本资料"信息
    data_dict = request.json
    nick_name = data_dict.get("nick_name")
    gender = data_dict.get("gender")
    signature = data_dict.get("signature")

    if not all([nick_name, gender, signature]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数有误")

    if gender not in (['MAN', 'WOMAN']):
        return jsonify(errno=RET.PARAMERR, errmsg="参数有误")

    # 3. 更新并保存数据
    user.nick_name = nick_name
    user.gender = gender
    user.signature = signature
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="保存数据失败")

    # 将 session 中保存的数据进行实时更新
    session["nick_name"] = nick_name

    # 4. 返回响应
    return jsonify(errno=RET.OK, errmsg="更新成功")


@profile_blu.route('/info')
@user_login_data
def user_info():
    """个人中心显示"""
    user = g.user
    if not user:
        return redirect("/")
    data = {
        "user": user.to_dict()
    }
    return render_template("news/user.html",data=data)