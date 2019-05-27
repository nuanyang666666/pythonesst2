import functools

from flask import session, g
from sqlalchemy import and_

from sqlalchemy.orm import sessionmaker



from code1.app import db
from code1.app.models.models import User


def login_user_data(view_func):
    @functools.wraps(view_func)
    def wrapper(*args, **kwargs):
        user_id = session.get('user_id')

        if user_id:
            # 判断用户名字是否存在
            try:

                # 判断用户是否存在
                user = db.session.query(User).filter(User.user_id == user_id).one()
                print(user.user_id,'---------------------------')
            except:
                print('登录的用户不存在，请重新输入')

        g.user = user
        return view_func(*args, **kwargs)
    return wrapper

