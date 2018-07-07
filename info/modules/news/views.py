from flask import abort, jsonify
from flask import current_app
from flask import g
from flask import render_template
from flask import request


from info import constants, db
from info.models import News, Comment
from info.utils.common import user_login_data
from info.utils.response_code import RET
from . import news_blu


@news_blu.route("/news_comment",methods=["POST"])
@user_login_data
def news_comment():
    """评论新闻和回复其他人的评论(一个视图函数实现两个功能)"""
    # 0:获取用户登入状态
    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户不存在")

    # 1:获取请求参数
    news_id = request.json.get("news_id")
    comment_content = request.json.get("comment")
    parent_id = request.json.get("parent_id")  # 因为一条评论可能没有人回复,导致parent_id不存在

    # 2:判断参数
    if not all([news_id,comment_content]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    try:
        news_id = int(news_id)
        if parent_id:
            parent_id = int(parent_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询数据失败")

    if not news:
        return jsonify(errno=RET.NODATA, errmsg="新闻数据不存在")

    # 3:初始化一个评论模型,并赋值评论数据到数据库
    comment = Comment()
    comment.user_id = user.id
    comment.news_id = news_id
    comment.content = comment_content
    if parent_id:
        comment.parent_id = parent_id

    # 4:添加到数据库
    try:
        db.session.add(comment)
        db.session.commit()
    except Exception as e:
        comment_content.logger.error(e)
        db.session.rollback()

    # 5:再查询数据库的评论数据,返回给前端

    return jsonify(errno=RET.OK, errmsg="OK", data=comment.to_dict())


@news_blu.route("/news_collect", methods=['POST'])
@user_login_data
def news_collect():
    """新闻收藏"""
    # 0. 取出用户(装饰器)
    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户不存在")

    # 1. 接受参数
    news_id = request.json.get("news_id")
    action = request.json.get("action")

    # 2. 判断参数
    if not all([news_id,action]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    if action not in ["collect","cancel_collect"]:
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    try:
        news_id = int(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    # 3. 查询新闻,并判断新闻是否存在
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询数据失败")

    if not news:
        return jsonify(errno=RET.NODATA, errmsg="新闻数据不存在")

    if action == "cancel_collect":
        # 4. 取消收藏
        if news in user.collection_news:
            user.collection_news.remove(news)

    else:
        # 4. 收藏新闻
        if news not in user.collection_news:
            user.collection_news.append(news)

    return jsonify(errno=RET.OK, errmsg="保存成功")


@news_blu.route('/<int:news_id>')
@user_login_data
def news_detail(news_id):
    """
    新闻详情
    :param news_id:
    :return:
    """
    # 1:采用装饰器和g变量获取用户登入的信息
    user = g.user

    # 2:右侧的新闻排行的逻辑
    news_list = []
    try:
        # 搜索数据库 : 按照最高点记率,排序6个
        news_list = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS).all()
    except Exception as e:
        current_app.logger.error(e)

    # 因为news_list是模型对象
    news_dict_li = []
    # 遍历对象列表,将对象的字典添加到字典列表中
    for news in news_list:
        news_dict_li.append(news.to_basic_dict())

    # 3:给详情页查询对应的新闻数据
    news = None
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)

    if not news:
        # 新闻详情数据如果查不出数据,就抛出404错误
        abort(404)

    # 4:更新新闻的点击次数
    news.clicks += 1

    # 5:是否收藏的按钮展示
    is_collected = False
    if user:
        # 因为用户和新闻是多对多的关系，会有中间表，表示当前新闻是否在用户的收藏新闻表里
        # collection_news 后面可以不用加all(),因为在表模型里面有dynamic，sqlalchemy会在使用的时候自动加载
        if news in user.collection_news:
            print(user.collection_news)
            is_collected = True

    # 6:用户评论的显示
    comments = []
    try:
       comments = Comment.query.filter(Comment.news_id==news_id).order_by(Comment.create_time.desc()).all()
    except Exception as e:
        current_app.logger.error(e)

    comment_list = []
    for item in comments:
        comment_dict = item.to_dict()
        comment_list.append(comment_dict)

    # TODO 为了详情也刷新后,评论内容消失


    data = {
        "user" : user.to_dict() if user else None,
        "new_dict_li" : news_dict_li,
        "news" : news.to_dict(),
        "is_collected" : is_collected,
        "comment" : comment_list
    }

    return render_template('news/detail.html', data=data)