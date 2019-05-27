class Config(object):
    # 添加秘钥
    SECRET_KEY = '123456'



class DEBUG(Config):
    #
    DEBUG = True



configure = {
    'CONFIG' : Config,
    'debug':DEBUG
}