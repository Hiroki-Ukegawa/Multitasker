import os

from flask import Flask
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from flask_app.config.settings import DevelopmentConfig, ProductionConfig
from flask_app.utils.template_filters import replace_newline, replace_newline_and_username


login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'ログインが必要です'

mail = Mail()

migrate = Migrate()

db = SQLAlchemy()

config_class = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}

def create_app():
    app = Flask(__name__)
    
    config_target = config_class[os.getenv('ENVIRONMENT', 'development')]
    app.config.from_object(config_target)

    app.config['MAIL_SERVER'] = 'smtp.sendgrid.net'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'apikey'
    app.config['MAIL_PASSWORD'] = os.environ.get('SENDGRID_API_KEY')
    app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER')

# Blueprintの登録
    from flask_app.views.admin import admin
    app.register_blueprint(admin)

    from flask_app.views.auth import auth
    app.register_blueprint(auth)

    from flask_app.views.todo import todo
    app.register_blueprint(todo)

# init_appによるアプリケーションとの紐付けを実行
    db.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

# template_filterの追加
    app.add_template_filter(replace_newline)
    app.add_template_filter(replace_newline_and_username)

    return app