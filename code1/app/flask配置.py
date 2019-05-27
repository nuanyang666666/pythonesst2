from flask import Flask, session, request

# 创建对象
from code1.app import configure

app = Flask(__name__)



# flask三种配置对象的方式
# 从对象中加载（常用）
app.config.from_object(configure['debug'])
# 第二种方式从配置文件中加载
# app.config.from_pyfile('CONFIG.ini')

# 第三中方式从环境变量中加载 必须修改环境变量里面
# app.config.from_envvar('env_config')
@app.before_first_request
def before_fire_request():
    print('before_first_request------在第一个请求钱执行')








    
@app.before_request
def before_request():
    print('before_request--------在每次请求前执行,如果在某修饰的函数中返回了一个响应，视图函数将不再被调用')
    print(request.remote_addr)
    ip = request.remote_addr
    print(ip)
    if ip=='127.0.0.1':
        return '不能访问该网页'





@app.after_request
def after_request(response):

    response.headers["Content-Type"] = "application/json"
    print('after_request-------如果没有抛出错误，在每次请求后执行，接受一个参数：视图函数做出的响应')
    return response

@app.teardown_request
def teardown_request(e):
    print(e)
    print('teardown_request--------在每次请求后执行，接受一个参数：错误信息，如果有相关错误抛出')


@app.route('/')
def index():
    session['name'] = '柳晋栋'
    print(session.get('name'))
    print(configure)

    return 'Hello World'




if __name__ == '__main__':
    app.run()

