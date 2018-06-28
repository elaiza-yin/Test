from flask import Flask
# 在终端输入: pip install flask-session,再去导入 Session
# 作用:可以用来指定 session 保存的位置
from flask.ext.session import Session
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.wtf import CSRFProtect
from redis import StrictRedis
from information.config import config


# 初始化数据库
# 在Flask很多拓展里面都可以可以初始化扩展的对象,然后再去调用 init_app 方法初始化
db = SQLAlchemy()


def creat_app(config_name):

    app = Flask(__name__)
    # 1.加载配置
    app.config.from_object(config[config_name])
    # 通过app初始化
    db.init_app(app)
    # 3.初始化 redis 存储对象
    redis_store = StrictRedis(host=config[config_name].REDIS_HOST, port=config[config_name].REDIS_PORT)
    # 4.开启当前项目的 CSRF 保护,只做服务器验证功能(所有的请求都会经过before_request请求勾子)
    CSRFProtect(app)
    # 5.设置session保存指定位置
    Session(app)

    return app

