import random
import re

from flask import abort, jsonify
from flask import current_app
from flask import make_response
from flask import request
from info import constants
from info import redis_store
from info.utils.response_code import RET
from libs.yuntongxun.sms import CCP
from . import passport_blu
from info.utils.captcha.captcha import captcha


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
    # 1. 获取参数:手机号,用户输入的图片验证码.图片验证码的编号
    params_dict = request.json  # params_dict = json.loads(request.data)
    mobile = params_dict.get('mobile')
    image_code = params_dict.get('image_code')
    image_code_id= params_dict.get('image_code_id')

    # 2. 校验参数(参数是否符合规则,判断是否有值)
    # 判断参数是否有值
    if not all([mobile,image_code,image_code_id]):
        # {'errno':'4100','errmsg':'参数有误'}
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
    result = CCP().send_template_sms(mobile,[sms_code_str,constants.SMS_CODE_REDIS_EXPIRES /60 ],1)
    if result == 0:
        # result = 0 表示验证码发送失败
        return jsonify(errno=RET.THIRDERR,errmsg="验证码d短信发送失败")

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
    # 1.取到参数(args:取到imageCodeUrl中 ? 后面的参数 )
    image_code_id = request.args.get('imageCodeId', None)

    # 2.判断参数是否有值
    if not image_code_id:
        return abort(403)

    # 3.生成图片验证码(导入captcha.py里的函数)
    name, text, image = captcha.generate_captcha()

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
