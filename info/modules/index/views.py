from flask import current_app, jsonify
from flask import render_template
# from info import redis_store
from flask import request
from flask import session

from info import constants
from info.models import User, News, Category
from info.utils.response_code import RET
from . import index_blu


@index_blu.route('/news_list')
def get_news_list():
    """首页新闻刷新"""
    # 1. 获取参数(get方式要用 args 获取浏览器?后缀的数据)
    cid = request.args.get("cid", "1")
    page = request.args.get("page", "1")
    per_page = request.args.get("per_page", "10")
    # 数据的测试
    print("分类:%s   第%s页  每页%s条数据" % (cid,page,per_page))
    # 2. 校验参数
    try:
        page = int(page)
        per_page = int(per_page)
        cid = int(cid)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR,errmsg="参数错误")

    # 3. 查询数据并分页
    filters = [News.status == 0]  # 添加"已审核通过"的条件===>0代表审核通过
    if cid != 1:  # 查询的不是"最新分类"的数据
        # 添加分类id的过滤
        filters.append(News.category_id == cid)
    try:
        # 返回一个Paginate对象，它包含指定范围内的结果
        paginate = News.query.filter(*filters).order_by(News.create_time.desc()).paginate(page,per_page,False)
        # Paginate对象有一下几个方法:取到当前页面的数据
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
            print("判断用户是否登入的查询:%s" % user)  # 测试:打印的是:<User 24>对象
        except Exception as e:
            current_app.logger.error(e)

    # 二:右侧的新闻排行的逻辑(new_list是模型数据,也是对象)
    news_list = []
    try:
        # 搜索数据库 : 按照最高点记率,排序6个
        news_list = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
        print("排行的新闻查询:%s" %news_list)  # 打印的是对象
    except Exception as e:
        current_app.logger.error(e)

    # 因为news_list是模型对象,要转化成字典传给index.html
    news_dict_li = []
    # 遍历对象列表,将对象的字典添加到字典列表中
    for news in news_list:
        news_dict_li.append(news.to_basic_dict())

    # 三:分类数据的新闻的显示(查询分类数据,通过模板形式渲染出来)
    categories = Category.query.all()

    category_li = []
    for category in categories:
        category_li.append(category.to_dict())

    # 一和二和三共同存放数据的data字典容器
    data = {
        #  实例对象user去调用函数to_dict()
        "user" : user.to_dict() if user else None,
        "news_dict_li" : news_dict_li,
        "category_li" : category_li
    }

    return render_template('/news/index.html',data=data)


# 在打开网页的时候，浏览器会默认去请求根路径+favicon.ico作网站标签的小图标
# send_static_file 是 flask 去查找指定的静态文件所调用的方法
@index_blu.route('/favicon.ico')
def favicon():
    return current_app.send_static_file('news/favicon.ico')