from information.info import redis_store
from . import index_blu


@index_blu.route("/")
def index():
    # 需求:向redis中保存一个值
    # 如果redis_store. 没有智能提示可以到 __init__.py里的redis_store 后面加个变量注释 ==> type:StrictRedis
    redis_store.set('name','elaiza')

    return "阿根廷"