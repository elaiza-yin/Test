from redis import StrictRedis
class Config(object):
    """1.项目配置"""
    DEBUG = True

    """
    生成方法: import os , base64
              base64.b64encoode(os.urandom(48))
    """
    # 5.6 使用Session就要设置 SECRET_KEY
    SECRET_KRY = 'q4fMRVYRGIf4PArUvH+lzfY1MyUnXO5uiHMaguO05iX4+F+4eqLQWUxi0RigqomR'

    # 2.为 Mysql 添加配置
    SQLALCHEMY_DATABASE_URI = 'mysql://root:mysql@127.0.0.1:3306/information'
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    # 3.为 Redis 配置
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379

    # 5.1 Session保存配置
    SESSION_TYPE = 'redis'
    # 5.2 开启Session签名
    SESSION_USE_SIGNER = True
    # 5.3 指定Session保存到redis
    SESSION_REDIS = StrictRedis(host=REDIS_HOST, port=REDIS_PORT)
    # 5.4 设置需要过期
    SESSION_PERMANENT = False
    # 5.5 设置过期时间
    PERMANENT_SESSION_LIFETIME = 86400 * 2