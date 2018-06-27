from flask.ext.wtf import CSRFProtect
from redis import StrictRedis
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy


class Config(object):
    """1.项目配置"""
    DEBUG = True

    # 2.为 Mysql 添加配置
    SQLAlchemy_DATABASE_URL = 'mysql://root:mysql@127.0.0.1:3306/information'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 3.为 Redis 配置
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379


app = Flask(__name__)

# 1.加载配置
app.config.from_object(Config)
# 2.初始化数据库
db = SQLAlchemy(app)
# 3.初始化 redis 存储对象
redis_store = StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)
# 4.开启当前项目的 CSRF 保护,只做服务器验证功能(所有的请求都会经过before_request请求勾子)
CSRFProtect(app)


@app.route("/")
def index():
    return "index"


if __name__ == "__main__":
    app.run()
