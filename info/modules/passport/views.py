from flask import abort
from flask import current_app
from flask import make_response
from flask import request
from information.info import constants
from information.info import redis_store
from . import passport_blu
from information.info.utils.captcha.captcha import captcha


@passport_blu.route('/image_code')
def get_image_code():
    """
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
        # constants.IMAGE_CODE_REDIS_EXPIRES 是过期时间,不能写死,300秒存在constants
        redis_store.set('ImageCodeId_' + image_code_id, text, constants.IMAGE_CODE_REDIS_EXPIRES )

    except Exception as e:
        current_app.logger.error(e)  # flask 自带的打印日志
        abort(500)

    # 5.返回验证码图片
    response = make_response(image)
    response.headers['Content-Type'] = 'image/jpg'
    return response
