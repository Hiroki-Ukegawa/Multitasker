from flask import Markup
from flask_login import current_user

def replace_newline(text):
    return Markup(text.replace('\r\n', '<br>'))

def replace_newline_and_username(text):
    return Markup(text.replace('\r\n', '<br>').replace('ユーザー', current_user.username))