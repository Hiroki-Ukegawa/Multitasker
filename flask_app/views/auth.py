import pytz
from datetime import datetime

from flask import Blueprint, flash, render_template, redirect, request, session, url_for 
from flask_login import login_required, login_user, logout_user

from flask_app import db
from flask_app.forms import RegisterForm, LoginForm
from flask_app.models import User, Task


auth = Blueprint('auth', __name__, url_prefix='')


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User(
            username = form.username.data,
            email = form.email.data,
            password = form.password.data
        )
        with db.session.begin(subtransactions=True):
            user.create_new_user()
        db.session.commit()
        flash('ユーザー登録が完了しました')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User.select_user_by_email(form.email.data)
        if user and user.is_active and not user.admin_password and user.validate_password(form.password.data):
            login_user(user, remember=True)
            if user.login_count == 0:
                datetime_now = datetime.now(pytz.timezone('Asia/Tokyo'))
                today = datetime_now.date()
                task = Task(
                    user_id = user.id,
                    taskname = 'マルチタスクの第一歩',
                    description = '【チュートリアル】\r\nまずは「新規作成」からタスクを作成しましょう。\r\nタスク毎に設定可能な0〜100%の完了度は、' + user.username + 'さんが複数のタスクを切り替えながら、少しずつ同時に進めることをサポートします。',
                    due = today
                )
                with db.session.begin(subtransactions=True):
                    user.login_count += 1
                    task.create_new_task()
                db.session.commit()
            else:
                with db.session.begin(subtransactions=True):
                    user.login_count += 1
                    user.update_at = datetime.now(pytz.timezone('Asia/Tokyo'))
                db.session.commit()
            next = request.args.get('next')
            if not next:
                next = url_for('todo.home')
            return redirect(next)
        elif not user:
            flash('登録のないメールアドレスです')
        elif not user.is_active:
            flash('アカウントがロックされているか、退会済のユーザーです')
        elif not user.validate_password(form.password.data):
            flash('パスワードが間違っています')
    return render_template('auth/login.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('todo.home'))