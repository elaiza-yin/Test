from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from info import creat_app, db, models

# manager.py 是程序启动的入口,只关心启动的相关参数以及内容,不关心具体该如何创建app或者相关的业务逻辑


# 通过指定的配置名字创建对应配置的app
from info.models import User

app = creat_app('development')
# 设置成命令行执行代码的方式:manager
manager = Manager(app)
# 数据库的迁移
Migrate(app, db)
manager.add_command('db', MigrateCommand)


# 命令行集成管理员用户
@manager.option('-n','-name',dest="name")
@manager.option('-p','-password',dest="password")
def createsuperuser(name,password):
    if not all ([name,password]):
        print("参数不足")

    user = User()
    user.nick_name = name
    user.mobile = name
    user.password = password
    user.is_admin = True

    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(e)
    print("添加成功")


if __name__ == "__main__":
    # 如果想右键运行:可以将runserver添加到 manager.py的 Script parameters(在Edit Configurations里)
    manager.run()
