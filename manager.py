from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy


class Config(object):
    """项目配置"""
    DEBUG = True

    # 为 Mysql 添加配置
    SQLAlchemy_DATABASE_URL = 'mysql://root:mysql@127.0.0.1:3306/information'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


app = Flask(__name__)

# 加载配置
app.config.from_object(Config)
# 初始化数据库
db = SQLAlchemy(app)


@app.route("/")
def index():
    return "index"


if __name__ == "__main__":
    app.run()
