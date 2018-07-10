import logging
from logging.handlers import RotatingFileHandler
from flask import Flask
# 在终端输入: pip install flask-session,再去导入 Session
# 作用:可以用来指定 session 保存的位置
from flask import g
from flask import render_template
from flask.ext.session import Session
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.wtf import CSRFProtect
from flask.ext.wtf.csrf import generate_csrf
from redis import StrictRedis

from config import config


# 在Flask很多拓展里面都可以可以初始化扩展的对象,然后再去调用 init_app 方法初始化
# 初始化数据库
db = SQLAlchemy()

# 变量的注释
redis_store = None  # type: StrictRedis


def setup_log(config_name):
    """日志文件配置"""
    # 设置日志的记录等级
    logging.basicConfig(level=config[config_name].LOG_LEVEL)  # 调试debug级
    # 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
    file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024 * 1024 * 100, backupCount=10)
    # 创建日志记录的格式 日志等级 输入日志信息的文件名 行数 日志信息
    formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
    # 为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)
    # 为全局的日志工具对象（flask app使用的）添加日志记录器
    logging.getLogger().addHandler(file_log_handler)


def creat_app(config_name):
    # 配置日志,并且传入配置名字,以便能获取到指定配置所对应的日志等级
    setup_log(config_name)
    # 创建Flask对象
    app = Flask(__name__)
    # 1.加载配置
    app.config.from_object(config[config_name])
    # 通过app初始化
    db.init_app(app)
    # 3.初始化 redis 存储对象
    global redis_store
    redis_store = StrictRedis(host=config[config_name].REDIS_HOST, port=config[config_name].REDIS_PORT,decode_responses=True)
    # 4.开启当前项目的 CSRF 保护,只做服务器验证功能(所有的请求都会经过before_request请求勾子)
    CSRFProtect(app)
    # 5.设置session保存指定位置
    Session(app)

    # 添加自定义过滤器
    from info.utils.common import do_index_class
    app.add_template_filter(do_index_class ,"index_class")

    from info.utils.common import user_login_data
    @app.errorhandler(404)
    @user_login_data
    def page_not_found(e):
        user = g.user
        data = {"user" : user.to_dict() if user else None}
        return render_template("news/404.html",data=data)

    @app.after_request
    def after_request(response):
        # 生成随机的csrf_token的值
        csrf_token = generate_csrf()
        # 设置一个cookie
        response.set_cookie("csrf_token",csrf_token)
        return response

    # 注册蓝图
    # 什么时候用什么时候导入:index_blu(避免循环导入)
    from info.modules.index import index_blu
    app.register_blueprint(index_blu)

    from info.modules.passport import passport_blu
    app.register_blueprint(passport_blu)

    from info.modules.news import news_blu
    app.register_blueprint(news_blu)

    from info.modules.profile import profile_blu
    app.register_blueprint(profile_blu)

    return app

