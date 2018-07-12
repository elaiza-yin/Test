from flask import abort, jsonify
from flask import current_app
from flask import g
from flask import render_template
from flask import request

from info import constants, db
from info.models import News, Comment, CommentLike
from info.utils.common import user_login_data
from info.utils.response_code import RET
from . import news_blu


@news_blu.route("/comment_like",methods=["POST"])
@user_login_data
def comment_like():
    """点赞和取消点赞"""
    # 0:点赞也需要用户登入
    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户不存在")

    # 1:获取请求参数
    comment_id = request.json.get("comment_id")
    news_id = request.json.get("news_id")
    action = request.json.get("action")

    # 2:判断参数
    if not all([news_id, comment_id,action]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    if action not in ["add","remove"]:
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    try:
        comment_id = int(comment_id)
        news_id = int(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    try:
        # 查询评论是否存在
        comment = Comment.query.get(comment_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询数据失败")

    if not comment:
        return jsonify(errno=RET.NODATA, errmsg="评论不存在")

    # 3:点赞和取消点赞操作
    if action == "add":
        # 点赞评论
        # 查询指定的点赞模型
        comment_like_model = CommentLike.query.filter(CommentLike.user_id==user.id,CommentLike.comment_id==comment.id).first()
        if not comment_like_model:
            comment_like_model = CommentLike()
            comment_like_model.user_id = user.id
            comment_like_model.comment_id = comment_id
            db.session.add(comment_like_model)
            comment.like_count += 1

    else:
        # 取消点赞
        # 查询指定的点赞模型
        comment_like_model = CommentLike.query.filter(CommentLike.user_id==user.id,CommentLike.comment_id==comment.id).first()
        if comment_like_model:
            db.session.delete(comment_like_model)
            comment.like_count -= 1

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库操作失败")

    return jsonify(errno=RET.OK, errmsg="OK")


@news_blu.route("/news_comment",methods=["POST"])
@user_login_data
def news_comment():
    """评论新闻和回复其他人的评论(一个视图函数实现两个功能)"""
    # 0:评论也需要用户登入
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

    # 5:再查询数据库的评论数据,返回给前端:comment.to_dict()

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

    # 6:当前新闻所有的评论(为了详情也刷新后,评论内容消失)
    comments = []
    try:
       comments = Comment.query.filter(Comment.news_id==news_id).order_by(Comment.create_time.desc()).all()
    except Exception as e:
        current_app.logger.error(e)

    # 7:需求:查询当前用户在当前的新闻点赞哪些评论
    # 7.1 查询出当前新闻的所有评论
    # 7.2 再查询被当前用户所点赞的评论
    comment_like_ids = []
    if g.user:
        # 如果当前用户已登录
        try:
            comment_ids = [comment.id for comment in comments]
            if len(comment_ids) > 0:
                # 取到当前用户在当前新闻的所有评论点赞的记录
                comment_likes = CommentLike.query.filter(CommentLike.comment_id.in_(comment_ids),
                                                         CommentLike.user_id == g.user.id).all()
                # 取出记录中所有的评论id
                comment_like_ids = [comment_like.comment_id for comment_like in comment_likes]
        except Exception as e:
            current_app.logger.error(e)

    comment_dict_li = []
    for comment in comments:
        comment_dict = comment.to_dict()
        # 给评论的comment_dict字典添加一个键值对:False默认代表没有点赞
        comment_dict['is_like'] = False
        if comment.id in comment_like_ids:
            comment_dict['is_like'] = True
        comment_dict_li.append(comment_dict)

    is_followed = False
    # if 当前新闻有作者,并且 当前用户已登入
    if news.user and user:
        # 判断 user 是否关注这个 新闻作者
        if news.user in user.followed:
            is_followed = True

    data = {
        "user" : user.to_dict() if user else None,
        "new_dict_li" : news_dict_li,
        "news" : news.to_dict(),
        "is_collected" : is_collected,
        "is_followed":is_followed,
        "comments" : comment_dict_li
    }

    return render_template('news/detail.html', data=data)