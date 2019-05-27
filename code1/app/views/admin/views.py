from flask import render_template, redirect, request
from sqlalchemy.orm import sessionmaker

# 引入蓝图
from code1.app import db
from code1.app.models.models import User
from . import admin_blu

# 使用蓝图添加路由
@admin_blu.route('/')
def index1():
    # 访问 / 就重定向到index.html
    return redirect('index.html')


@admin_blu.route('/index.html')
def index2():
    # 创建session对象
    # DBSession = sessionmaker(bind=engine)  # 创建与数据库的会话，返回的是一个类
    # session = DBSession()  # 生成会话对象
    # # 查询user表中所有的用户数据
    # all_user_info = session.query(User).all()
    # print(all_user_info)
    # # 关闭session
    # session.close()

    return render_template('admin/index.html')


@admin_blu.route('/tables.html')
def tables():
    """显示用户信息的页面"""
    # 分页功能
    # 要分页的数量
    page_size = 5 # 每页显示五个
    # page_index = 1 # 从第几页开始
    # 获取点击的页数是第几页
    page_index = int(request.args.get('page',1))
    # 参数一是从第几页开始 参数二是每页显示多少个 参数三 如果出现错误返回404错误，默认值是True
    pagination = User.query.paginate(page = page_index,per_page=page_size, error_out=False)

    # 获取所有用户的信息
    all_user_info = pagination.items
    print(all_user_info)

    # print(all_user_info)
    # 关闭session
    db.session.close()

    return render_template('admin/tables.html', user_infos=all_user_info, pagination=pagination)


@admin_blu.route('/testfilter.html')
def testfilter():
    """显示用户信息的页面"""
    var1 = '<em>hello</em>'
    var2 = 'hEllo world hehe'

    return render_template('admin/testfilter.html', var1=var1, var2=var2)


class Student():
    def __init__(self, name):
        self.name = name


@admin_blu.route('/control.html')
def testcontrol():
    """显示用户信息的页面"""
    # stu = Student('小明')
    stu = None
    stu1 = Student('小红')
    stu2 = Student('小明')
    stu3 = Student('小绿')
    stu4 = Student(None)
    stus = [stu1, stu2, stu3, stu4]

    return render_template('admin/control.html', stu=stu, stus=stus)
