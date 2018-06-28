import logging

from flask import current_app
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from information.info import creat_app ,db


# 通过指定的配置名字创建对应配置的app
app = creat_app('development')
# 设置成命令行执行代码的方式:manager
# 作用:可以添加 数据库迁移 的功能,因为要用到命令的方式
manager = Manager(app)
# 数据库的迁移
Migrate(app, db)  # 将app 与 db 关联
manager.add_command('db', MigrateCommand)  # 将迁移命令添加到manager


@app.route("/")
def index():
    # session['name'] = 'elaiza'  # 测试redis数据

    # 测试打印日志
    logging.debug('测试debug')
    logging.warning('测试warning')
    logging.error('测试error')
    logging.fatal('测试fatal')

    # 当前应用程序的logger会根据应用程序的调试状态去调整日志级别
    # 在flask下面输出日志
    current_app.logger.error('测试error')
    return "阿根廷"


if __name__ == "__main__":
    # 如果想右键运行:可以将runserver添加到 manager.py的 Script parameters(在Edit Configurations里)
    manager.run()
