# 共用的自定义工具类
import functools

from flask import current_app
from flask import g
from flask import session

from info.models import User


def do_index_class(index):
    """返回指定索引对应的类名(过滤器的定义)"""
    if index == 0:
        return "first"
    elif index == 1:
        return  "second"
    elif index == 2:
        return "third"

    return ""


# 用户登入信息的装饰器和g变量容器,方便视图函数去取用户登入的信息
def user_login_data(f):
    @functools.wraps(f)
    def wrapper(*args,**kwargs):
        user_id = session.get("user_id", None)
        user = None
        if user_id:
            try:
                user = User.query.get(user_id)
            except Exception as e:
                current_app.logger.error(e)
        g.user = user
        return f(*args,**kwargs)
    return wrapper
