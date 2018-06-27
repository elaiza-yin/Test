from flask.ext.wtf import CSRFProtect
from redis import StrictRedis
from flask import Flask, session
from flask.ext.sqlalchemy import SQLAlchemy
# 在终端输入: pip install flask-session,再去导入 Session
# 作用:可以用来指定 session 保存的位置
from flask_session import Session


class Config(object):
    """1.项目配置"""
    DEBUG = True

    """
    生成方法: import os , base64
              base64.b64encoode(os.urandom(48))
    """
    # 5.6 使用Session就要设置 SECRET_KEY
    SECRET_KRY = 'q4fMRVYRGIf4PArUvH+lzfY1MyUnXO5uiHMaguO05iX4+F+4eqLQWUxi0RigqomR'

    # 2.为 Mysql 添加配置
    SQLAlchemy_DATABASE_URL = 'mysql://root:mysql@127.0.0.1:3306/information'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 3.为 Redis 配置
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379

    # 5.1 Session保存配置
    SESSION_TYPE = 'redis'
    # 5.2 开启Session签名
    SESSION_USE_SIGNER = True
    # 5.3 指定Session保存到redis
    SESSION_REDIS = StrictRedis(host=REDIS_HOST, port=REDIS_PORT)
    # 5.4 设置需要过期
    SESSION_PERMANENT = False
    # 5.5 设置过期时间
    PERMANENT_SESSION_LIFETIME = 86400 * 2


app = Flask(__name__)

# 1.加载配置
app.config.from_object(Config)
# 2.初始化数据库
db = SQLAlchemy(app)
# 3.初始化 redis 存储对象
redis_store = StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)
# 4.开启当前项目的 CSRF 保护,只做服务器验证功能(所有的请求都会经过before_request请求勾子)
CSRFProtect(app)
# 5.设置session保存指定位置
Session(app)


@app.route("/")
def index():
    session['name'] = 'elaiza'
    return "index"


if __name__ == "__main__":
    app.run()
