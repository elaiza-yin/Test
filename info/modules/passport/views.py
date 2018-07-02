import random
import re
from datetime import datetime

from flask import abort, jsonify
from flask import current_app
from flask import make_response
from flask import request
from flask import session

from info import constants, db
from info import redis_store
from info.models import User
from info.utils.response_code import RET
from libs.yuntongxun.sms import CCP
from . import passport_blu
from info.utils.captcha.captcha import captcha


@passport_blu.route('/logout',methods=["POST"])
def logout():
    """退出登入也算修后端数据,可以用POST方法"""
    session.pop('user_id',None)
    session.pop('mobile',None)
    session.pop('nick_name',None)

    return jsonify(errno=RET.OK,errmsg="退出成功")


@passport_blu.route('/login' ,methods=["POST"])
def login():
    """
    登入
    1. 获取参数
    2. 校验参数
    3. 校验密码是否正确
    4. 保存用户的登入信息
    5. 返回响应
    :return:
    """
    # 1. 获取参数
    params_dict = request.json
    mobile = params_dict.get('mobile')
    password = params_dict.get('password')

    # 2. 校验参数
    if not all([mobile,password]):
        return jsonify(errno=RET.PARAMERR,errmsg="参数错误")
    # 校验电话号码格式
    if not re.match('1[356789]\\d{9}', mobile):
        return jsonify(errno=RET.PARAMERR, errmsg='手机号码格式不正确')

    # 3. 校验密码是否正确
    # 先查询当前是否有指定的手机号的用户
    try:
        user = User.query.filter(User.mobile == mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="数据查询错误")
    # 判断用户是否存在
    if  not user:
        return jsonify(errno=RET.NODATA,errmsg="用户不存在")

    # 校验登入的密码是否和当前用户输入的密码是否一致
    if not user.check_passowrd(password):
        return jsonify(errno=RET.PWDERR,errmsg="用户或密码错误")

    # 4. 保存用户的登入状态
    session["user_id"] = user.id
    session["mobile"] = user.mobile
    session["nick_name"] = user.nick_name

    # 5. 响应
    return jsonify(errno=RET.OK,errmsg="登入成功")


@passport_blu.route('/register', methods=["POST"])
def register():
    """
    注册的逻辑
    1. 获取参数
    2. 校验参数
    3. 获取服务器保存的真实短信验证码内容
    4. 检验用户输入的短信验证码内容和真实短信验证码内容是否一样
    5. 如果一致,初始化 User 模型,并且赋值属性(给info_user表的字段添加数据)
    6. 将 user 模型添加到数据库
    7. 返回响应
    :return:
    """
    # 1. 获取参数
    param_dict = request.json
    mobile = param_dict.get('mobile')
    smscode = param_dict.get('smscode')
    password = param_dict.get('password')

    # 2. 校验参数
    if not all([mobile,smscode,password]):
        return jsonify(errno=RET.PARAMERR,errmsg='参数有误')

    if not re.match('1[356789]\\d{9}',mobile):
        return jsonify(errno=RET.PARAMERR,errmsg='手机号码格式不正确')

    # 3. 获取服务器保存的真实短信验证码内容
    try:
        real_sms_code = redis_store.get("SMS_" + mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg='短信验证码查询失败')

    if not real_sms_code:
        return jsonify(errno=RET.NODATA,errmsg='验证码已过期')

    # 4. 检验用户输入的短信验证码内容和真实短信验证码内容是否一样
    if real_sms_code != smscode:
        return jsonify(errno=RET.DATAERR,errmsg='验证码输入有误')

    # 5. 如果一致,初始化 User 模型,并且赋值属性(给info_user表的字段添加数据)
    user = User()
    user.mobile = mobile
    # 暂时没有昵称,使用电话当昵称
    user.nick_name = mobile
    # 记录用户最后一次登陆时间
    user.last_login = datetime.now()
    # 对密码做加密处理
    user.password = password

    # 6. 添加到数据库
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR,errmsg='数据保存失败')

    # 7. 往session中保存数据就表示当前是 "已登入状态"
    session["user_id"] = user.id
    session["mobile"] = user.mobile
    session["nick_name"] = user.nick_name

    # 8. 返回响应
    return jsonify(errno=RET.OK ,errmsg='注册成功')


@passport_blu.route('/sms_code',methods=['POST'])
def send_sms_code():
    """
    发送短信的逻辑(步骤):
    1. 获取参数:手机号,用户输入的图片验证码.图片验证码的编号
    2. 校验参数(参数是否符合规则,判断是否有值)
    3. 先从redis中取出真实的图形验证码内容
    4. 与用户的图形验证码内容进行对比,如果不一致,那么返回验证码输入错误
    5. 如果一致,生成短信验证码的内容(要是随机的数据)
    6. 发送短信验证
    7. 告知发送结果
    :return:
    """
    ######## 下方一行代码用于测试 : 直接表示发送成功########
    # return jsonify(errno=RET.OK, errmsg='发送成功')

    # 1. 获取参数:手机号,用户输入的图片验证码,图片验证码的编号
    params_dict = request.json  # params_dict = json.loads(request.data) 获取参数的第二种方法
    mobile = params_dict.get('mobile')
    image_code = params_dict.get('image_code')
    image_code_id= params_dict.get('image_code_id')

    # 2. 校验参数(参数是否符合规则,判断是否有值)
    # 判断参数是否有值
    if not all([mobile,image_code,image_code_id]):
        # 返回的jsonify格式数据:{'errno':'4100','errmsg':'参数有误'}
        return jsonify(errno=RET.PARAMERR,errms='参数有误')
    # 判断用户输入的手机号码是否正确
    if not re.match('1[356789]\\d{9}',mobile):
        return jsonify(errno=RET.PARAMERR,errmsg='手机号码格式不正确')

    # 3. 先从redis中取出真实的图形验证码内容
    try:
        real_image_code = redis_store.get('ImageCodeId_' + image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg='数据查询失败')

    if not real_image_code:
        return jsonify(errno=RET.NODATA,errmsg='图片验证码过期')

    # 4. 与用户的图形验证码内容进行对比,如果不一致,那么返回验证码输入错误
    if real_image_code.upper() != image_code.upper():
        return jsonify(errno=RET.DATAERR,errmsg='验证码输入错误')

    # 5. 如果一致,生成短信验证码的内容(要是随机的数据)
    # 随机6位短信验证码 : 不够6位,前面补0
    sms_code_str = "%06d" % random.randint(0,999999)
    current_app.logger.debug('短信验证码内容是: %s' % sms_code_str)

    # 6. 发送短信验证码
    # result = CCP().send_template_sms(mobile,[sms_code_str,constants.SMS_CODE_REDIS_EXPIRES /60 ],1)
    # if result == 0:
    #     # result = 0 表示验证码发送失败
    #     return jsonify(errno=RET.THIRDERR,errmsg="验证码短信发送失败")

    # 6-7. 保存短信验证码到redis里
    try:
        redis_store.set("SMS_" + mobile,sms_code_str,constants.SMS_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg='短信验证码保存失败')

    # 7. 告知发送结果
    return jsonify(errno=RET.OK,errmsg='发送成功')


@passport_blu.route('/image_code')
def get_image_code():
    """
    图片验证码
    1.取到参数    print(image_code_id)
    2.判断参数是否有值
    3.生成图片验证码
    4.保存图片验证码到redis
    5.返回验证码图片
    :return:
    """
    # 1.取到参数(args:取到imageCodeUrl中 ? 后面的参数 ),没有会返回None
    image_code_id = request.args.get('imageCodeId', None)
    # print(image_code_id) 测试

    # 2.判断参数是否有值
    if not image_code_id:
        return abort(403)

    # 3.生成图片验证码(导入captcha.py里的函数)
    name, text, image = captcha.generate_captcha() # 用于注册按钮的测试,方便查看验证码
    current_app.logger.debug("图片验证码是: %s" % text)
    # 4.保存图片验证码到redis
    try:
        # constants.IMAGE_CODE_REDIS_EXPIRES 是过期时间,不能写死,300秒存在constants 的参数信息
        redis_store.set('ImageCodeId_' + image_code_id, text, constants.IMAGE_CODE_REDIS_EXPIRES )

    except Exception as e:
        current_app.logger.error(e)  # flask 自带的打印日志
        abort(500)

    # 5.返回验证码图片
    response = make_response(image)
    response.headers['Content-Type'] = 'image/jpg'
    return response
