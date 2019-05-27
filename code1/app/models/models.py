


# 用户表的类
from code1.app import db


class User(db.Model):
    # 表单的名字
    __tablename__='user'
    # 字段
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.String(50), nullable=False)
    user_name = db.Column(db.String(50), nullable=False)
    head_img = db.Column(db.String(200))
    short_description = db.Column(db.String(300))
    password = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=True)
    status = db.Column(db.Boolean, default=False)
    activekey = db.Column(db.String(50), nullable=True)


