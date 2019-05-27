# 从数据库查询数据 并且传给模板
import hashlib
import os
import uuid

import flask
from flask import render_template, url_for, redirect, request, make_response, session, g, current_app
from flask_mail import Message
from sqlalchemy import and_, or_
from werkzeug.exceptions import abort

from code1.app import db, mail
from code1.app.models.models import User
from code1.app.utils.commons.commons import login_user_data
from . import index_blu
from code1.app.utils.captcha import captcha

# LOGIN_FLAG = False  # 标记是否登录  默认没有登录


@index_blu.route('/profile_v7')
@login_user_data
def profile7():

    # 从cookie里获取是否登录成功的标记
    cookies = request.cookies
    # print(cookies)  # {'login_flag': 'success'}

    user = g.user
    print(user)
    # 判断该用户是否激活
    if user.status != 1:
        # 没有激活
        return '该用户没有激活，请重新激活（激活网址已发往你的邮箱，请注意查收）'
    if user:
        print(user.head_img)
        return render_template('index/profile.html', user_name=user.user_name, short_description=user.short_description, head_img=user.head_img)
    else:
        return '去<a href="http://127.0.0.1:5000/index/login.html">登录</a>'



@index_blu.route('/login.html')
def login():
    """显示登录页面"""
    return render_template('index/login.html')


@index_blu.route('/login', methods=['POST', 'GET'])
def login_vf():
    """处理登录验证的逻辑"""
    # 1获取get请求传来的用户名和密码
    # 请求对象request  是一个上下文对象 只能用于视图里
    # request.args 获取get请求传来的参数  得到的是一个字典 可以使用字典的语法 获取里面 的内容
    # print('request.args----', request.args)  # ImmutableMultiDict([('username', '123'), ('password', '321')])
    # request.form 获取post请求传来的参数 得到的是一个字典 可以使用字典的语法 获取里面 的内容
    # print('request.form----', request.form)  # ImmutableMultiDict([('username', '123'), ('password', '321')])
    # 获取用户名和密码
    username = request.form.get('username')
    password = request.form.get('password')
    print('username==', username)
    print('password==', password)
    # 2 根据用户名和密码去数据库查询 如果能查到 登录成功 如果不能 就提示登录失败
    try:
        user = db.session.query(User).filter(and_(User.user_id == username, User.password == password)).one()
    except:
        # 出现异常 没有查询到用户 登录失败
        # make_response可以返回一个response对象 这样用response对象 就可以去设置cookie
        response = make_response('登录失败了 username = %s password = %s' % (username, password))
        abort(404)

        # response.set_cookie('login_flag', 'fail')
        session['login_flag'] = 'fail'
    else:
        # LOGIN_FLAG = True
        # 登录成功  redirect返回的是一个response对象 可以设置cookie
        response = redirect(url_for('index.profile7'))

        # response.set_cookie('login_flag', 'success')
        session['login_flag'] = 'success'
        # 把user_id也存进来
        session['user_id'] = user.user_id

    finally:
        db.session.close()

    return response


@index_blu.route('/logout')
def logout():
    """退出登录"""
    # 获取response响应对象
    response = redirect(url_for("index.login"))
    # 把cookie登录相关的信息清除
    # response.delete_cookie('login_flag')
    # 清除session数据
    session.clear()

    return response


@index_blu.route("/register", methods=['GET', 'POST'])
def register():
    """显示注册页面 """
    # 判断请求方式
    if request.method == "POST":
        # print(request.form)
        # 提取 数据
        email = request.form.get("email")
        username = request.form.get("username")

        password = request.form.get("password")
        # 图片验证码
        captcha = request.form.get("captcha")

        # 只要有1个需要的数据，没有，那么就返回数据有误
        if not (email and username and password and captcha):
            # 返回对应的数据
            ret = {
                "status": 2,
                "msg": "输入数据有误，请重新输入"
            }
            return flask.jsonify(ret)

        # session里取出验证码
        session_captcha = session.get('captcha')
        # 判断验证码是否正确 转为小写判断 可以让用户忽略大小写输入
        if session_captcha.lower() != captcha.lower():
            # 返回对应的数据
            ret = {
                "status": 3,
                "msg": "验证码错误"
            }
            return flask.jsonify(ret)

        # 业务处理：注册用户

        # 去数据库查询 获取结果的第一条数据
        user_ret = db.session.query(User).filter(or_(User.email == email, User.user_id == username)).first()
        print(user_ret.user_id)
        if user_ret:
            # 2. 如果邮箱或者用户名已经存在，则不允许使用
            # 3. 返回对应的数据
            ret = {
                "status": 1,
                "msg": "邮箱或用户名已存在，请修改"
            }

        else:
            # 激活页面的跳转
            # 获取随机验证码 获取的是数字必须进行字符串的转换
            activekey = str(uuid.uuid1())
            print(activekey)
            activekey = activekey.replace('-', '')
            # 获取跳转的页面
            # request.host_url http://127.0.0.1:5000/
            active_addr = request.host_url + 'index/active?user_id={}&active_key={}'.format(username,activekey)

            msg = Message('官方注册', sender='ljd20000717@163.com', recipients=[email])
            # 这里的sender是发信人，写上你发信人的名字，比如张三。
            # recipients是收信人，用一个列表去表示。
            msg.body = '激活邮件'
            msg.html = '<a href={}>点我验证</a>完成账户激活,如果有问题请联系ljd,电话110'.format(active_addr)
            print(active_addr)
            mail.send(msg)
            # 未注册，那么则进行注册
            new_user = User(email=email, user_id=username, password=password, user_name=username, activekey=activekey)

            db.session.add(new_user)
            db.session.commit()

            # 3. 返回对应的数据
            ret = {
                "status": 0,
                "msg": "注册成功"
            }
        db.session.close()
        return flask.jsonify(ret)
    elif request.method == "GET":
        # 如果是get请求  就是请求页面
        return render_template("index/register.html")




@index_blu.route('/active')
def active():
    """激活功能"""
    # 获取get请求后面的数据
    user_id = request.args.get('user_id')
    print(user_id)

    # 获取激活码
    active_key = request.args.get('active_key')
    print(active_key)
    # 去数据库查询
    try:
        user = db.session.query(User).filter(and_(User.user_id==user_id, User.activekey==active_key))
    except Exception as e:
        print(e)
        response_str = '激活失败请重新注册'
    else:
        # 修改状态为1
        user.status = 1
        # 提交
        db.session.commit()
        print(user.status)
        response_str = '激活成功,<a href={}>登录</a>'.format(url_for('.login'))
    return response_str

# 编辑页面的跳转
@index_blu.route('/edit',methods = ['GET', 'POST'])
@login_user_data
def edit():
    # 判断是否有用户登录
    current_user = g.user
    if not g.user:
        return render_template(url_for('.login'))
    if request.method == 'GET':
        return render_template("index/edit.html", user = g.user)
    elif request.method == 'POST':
        # 获取编辑后的用户名字、密码、邮箱、文本内容
        user_name = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        content = request.form.get('content')


        # 获取头像信息
        f = request.files.get('image')
        if f:
            # 获取上传图片的后缀名字
            file_suffix = f.filename[f.filename.rfind("."):]

            # 根据图片的二进制数据获取md5加密的一个字符串最为保密的名字
            name_hash = hashlib.md5()
            name_hash.update(f.filename.encode('utf-8'))
            image_file_name = name_hash.hexdigest()

            # 图片保存的名字 = md5加密一个字符串 + 原后缀
            images_name = image_file_name + file_suffix
            # 图片在服务器中的路径
            image_path = os.path.join('/static/upload/imags', 'images'+images_name)
            print(image_path)

            # 存放图片的绝对路径
            path = current_app.root_path

            upload_path = os.path.join(path,'static/upload/images' + images_name)
            print(upload_path)

            # 以绝对路径上传图片
            f.save(upload_path)

            # 保存图片路径到数据库
            current_user.head_img = image_path
        # 修改用户信息 为新的信息
        current_user.user_name = user_name
        current_user.password = password
        current_user.email = email
        current_user.short_description = content

        # 提交数据
        db.session.commit()

        # 重新刷新编辑页面 显示新的信息
        return redirect(url_for(".edit"))


@index_blu.route('/forgot', methods=['POST','GET'])
def forgot():
    if request.method=='POST':
        #  获取刚刚要发送的邮箱
        email = request.form.get('email')
        print(email)
        # 去数据库中查找邮箱是否存在
        try:
            user = db.session.query(User).filter(User.email == email).one()
        except Exception as e:
            print(e)
            response =  """没有该邮箱请重新取输入<a href='url_for(".forgot")>"""
        else:
            # 获取该用户的用户名字
            user_name = user.user_name
            # 获取邮箱地址
            user_email = user.email
            # 获取发送邮件的地址
            active_addr = request.host_url + 'index/forgot?user_name={}&email={}'.format(user_name,user_email)
            # 发送邮件 这里的sender是发送邮件的人， recipients是要发送的邮箱
            msg = Message('修改密码', sender='ljd20000717@163.com' ,recipients=[user_email])
            # 发送的标题
            msg.body = '修改密码'
            # 内容
            msg.html= '<a href="{}">点击修改密码</a>'.format(active_addr)

            mail.send(msg)

            response = '发送成功请注意接受，<a href="{}">点击返回登录页面</a>'.format(url_for('.login'))
        return response


    elif request.method=='GET':

        return render_template('index/forgot.html')




@index_blu.route("/captcha")
def generate_captcha():
    # 1. 获取到当前的图片编号id
    captcah_id = request.args.get('id')

    # 2. 生成验证码
    # 返回保存的图片名字  验证码值  图片二进制内容
    name, text, image =captcha.generate_captcha()

    # print("注册时的验证码为：", name, text, image)  # 图片名字  验证码值  图片二进制内容

    # 3. 将生成的图片验证码值作为value，存储到session中
    session["captcha"] = text

    # 返回响应内容
    resp = make_response(image)
    # 设置内容类型
    resp.headers['Content-Type'] = 'image/jpg'
    return resp


