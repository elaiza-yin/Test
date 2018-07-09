from flask import g
from flask import redirect
from flask import render_template
from flask import request

from info.modules.profile import profile_blu
from info.utils.common import user_login_data


@profile_blu.route("/base_info",methods=["GET","POST"])
@user_login_data
def base_info():
    """个人中心的基本资料[GET 和 POST]"""
    user = g.user

    # 请求为GET时
    if request.method == "GET":
        data = {
            "user" : user.to_dict()
        }
        return render_template('news/user_base_info.html',data = data)

    # 请求为POST时:修改用户个人信息

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