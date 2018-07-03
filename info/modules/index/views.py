from flask import current_app, jsonify
from flask import render_template
# from info import redis_store
from flask import request
from flask import session

from info import constants
from info.models import User, News
from info.utils.response_code import RET
from . import index_blu


@index_blu.route('/news_list')
def get_news_list():
    """首页新闻刷新"""
    # 1. 获取参数
    cid = request.args.get("cid", "1")
    page = request.args.get("page", "1")
    per_page = request.args.get("per_page", "10")

    # 2. 校验参数
    try:
        page = int(page)
        per_page = int(per_page)
        cid = int(cid)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR,errmsg="参数错误")

    # 3. 查询数据并分页
    filters = []
    if cid != 1:  # 查询的不是最新的数据
        # 需要添加条件
        filters.append(News.category_id == cid)
    try:
        paginate = News.query.filter(*filters).order_by(News.create_time.desc()).paginate(page,per_page,False)
        # 取到当前页面的数据
        items = paginate.items  # 当前页数据(模型对象列表)
        total_page = paginate.pages  # 总页数
        current_page = paginate.page  # 当前页
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="数据查询错误")

    # 将模型对象列表转成字典列表
    news_dict_li = []
    for news in items:
        news_dict_li.append(news.to_basic_dict())
    data = {
        "total_page" : total_page,
        "current_page" : current_page,
        "news_dict_li" : news_dict_li
    }

    return jsonify(errno=RET.OK,errmsg="OK",data=data)


@index_blu.route("/")
def index():
    # 需求:向redis中保存一个值(也可以用于测试)
    # 如果redis_store. 没有智能提示可以到 __init__.py里的redis_store 后面加个变量注释 ==> type:StrictRedis
    # redis_store.set('name','elaiza')
    # redis_store.set('age',21)
    """
    显示首页
    :return:
    """
    # 一:(显示用户是否登入的逻辑)因为登入成功会有数据保存到session里
    user_id = session.get("user_id",None)
    user = None
    if user_id:
        try:
            user = User.query.get(user_id)
        except Exception as e:
            current_app.logger.error(e)

    # 二:右侧的新闻排行的逻辑(new_list是模型数据,也是对象)
    try:
        # 搜索数据库 : 按照最高点记率,排序6个
        news_list = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as e:
        current_app.logger.error(e)

    # 因为news_list是模型对象,要转化成字典传给index.html
    news_list_li = []
    # 遍历对象列表,将对象的字典添加到字典列表中
    for news in news_list:
        news_list_li.append(news.to_basic_dict())

    # 一和二共同存放数据的data字典容器
    data = {
        "user" : user.to_dict() if user else None,
        "news_dict_li" : news_list_li
    }

    return render_template('/news/index.html',data=data)


# 在打开网页的时候，浏览器会默认去请求根路径+favicon.ico作网站标签的小图标
# send_static_file 是 flask 去查找指定的静态文件所调用的方法
@index_blu.route('/favicon.ico')
def favicon():
    return current_app.send_static_file('news/favicon.ico')