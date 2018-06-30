from flask import current_app
from flask import render_template
# from info import redis_store
from . import index_blu


@index_blu.route("/")
def index():
    # 需求:向redis中保存一个值(也可以用于测试)
    # 如果redis_store. 没有智能提示可以到 __init__.py里的redis_store 后面加个变量注释 ==> type:StrictRedis
    # redis_store.set('name','elaiza')
    # redis_store.set('age',21)

    return render_template('/news/index.html')


# 在打开网页的时候，浏览器会默认去请求根路径+favicon.ico作网站标签的小图标
# send_static_file 是 flask 去查找指定的静态文件所调用的方法
@index_blu.route('/favicon.ico')
def favicon():
    return current_app.send_static_file('news/favicon.ico')