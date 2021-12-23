import os


class DevelopmentConfig:
    basedir = os.path.abspath(os.path.dirname(__name__))
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data_devlepment.sqlite')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ENV = 'development'
    DEBUG = True


class ProductionConfig:
    uri = os.environ.get('DATABASE_URL')
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if uri:
        SQLALCHEMY_DATABASE_URI = uri.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ENV = 'production'