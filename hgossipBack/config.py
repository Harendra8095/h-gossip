import os
from dotenv import load_dotenv
load_dotenv()

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY')
    POSTS_PER_PAGE = 25
    DEBUG = False
    ADMINS = ['Harendra']
    LANGUAGES = ['en', 'es']

class MailConfig():
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

class DbEngine_config():
    DB_DIALECT = os.environ.get('DB_DIALECT') or 'postgresql'
    DB_HOST = os.environ.get('DB_HOST') or 'localhost'
    DB_PORT = os.environ.get('DB_PORT') or '5432'
    DB_USER = os.environ.get('DB_USER') or 'postgres'
    DB_PASS = os.environ.get('DB_PASS') or 'postgres'
    DB_NAME = os.environ.get('DB_NAME') or 'h_gossipDB'
    if (os.environ.get('TEST') == '1'):
        DB_NAME = 'h_gossip_test'
    DB_URL = f'{DB_DIALECT}://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    DB_URL = os.environ.get('DATABASE_URL') if os.environ.get('DATABASE_URL') else DB_URL
    print(DB_URL)
    SQLALCHEMY_DATABASE_URI = DB_URL

class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False