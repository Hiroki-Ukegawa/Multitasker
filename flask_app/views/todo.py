import pytz
import random
from datetime import datetime

from flask import Blueprint, flash, jsonify, render_template, redirect, request, session, url_for 
from flask_login import current_user, login_required, logout_user
from flask_mail import Message as MessageOfMail

from flask_app import db, mail
from flask_app.forms import UserForm, ChangePasswordForm, DeleteUserForm, TaskForm, ContactForm
from flask_app.models import Contact, User, Task, Message


todo = Blueprint('todo', __name__, url_prefix='')


@todo.route('/')
def home():
    datetime_now = datetime.now(pytz.timezone('Asia/Tokyo'))
    today = datetime_now.date()
    tasks = []
    form = TaskForm(request.form)
    message = None
    if current_user.is_authenticated:
        user_id = current_user.get_id()
        tasks = Task.select_uncompleted_tasks_by_user_id(user_id)
        message_type = random.randint(1, 6)
        message = Message.select_message_by_message_type(message_type, datetime_now)
    return render_template('todo/home.html', today=today, tasks=tasks, form=form, message=message)


@todo.route('/create_task', methods=['GET', 'POST'])
@login_required
def create_task():
    form = TaskForm(request.form)
    if request.method == 'POST' and form.validate():
        user_id = current_user.get_id()
        task = Task(
            user_id = user_id,
            taskname = form.taskname.data,
            description = form.description.data,
            due = form.due.data
        )
        with db.session.begin(subtransactions=True):
            task.create_new_task()
        db.session.commit()
        return redirect(url_for('todo.home'))
    return render_template('todo/create_task.html', form=form)

@todo.route('/update_task/<int:id>', methods=['GET', 'POST'])
@login_required
def update_task(id):
    task = Task.query.get(id)
    if not task.user_id == int(current_user.get_id()):
        return redirect(url_for('todo.home'))
    form = TaskForm(request.form)
    if request.method == 'POST' and form.validate():
        with db.session.begin(subtransactions=True):
            task.taskname = form.taskname.data
            task.description = form.description.data
            task.due = form.due.data
            task.update_at = datetime.now(pytz.timezone('Asia/Tokyo'))
        db.session.commit()
        return redirect(url_for('todo.home'))
    return render_template('todo/update_task.html', task=task, form=form) 

@todo.route('/delete_uncompleted_task/<int:id>')
@login_required
def delete_uncompleted_task(id):
    task = Task.query.get(id)
    if not task.user_id == int(current_user.get_id()):
        return redirect(url_for('todo.home'))
    with db.session.begin(subtransactions=True):
        task.delete_task()
    db.session.commit()
    return redirect(url_for('todo.home'))

@todo.route('/delete_completed_task/<int:id>')
@login_required
def delete_completed_task(id):
    task = Task.query.get(id)
    if not task.user_id == int(current_user.get_id()):
        return redirect(url_for('todo.completed_tasks'))
    with db.session.begin(subtransactions=True):
        task.delete_task()
    db.session.commit()
    return redirect(url_for('todo.completed_tasks'))

@todo.route('/complete_task/<int:id>')
@login_required
def complete_task(id):
    task = Task.query.get(id)
    if not task.user_id == int(current_user.get_id()):
        return redirect(url_for('todo.home'))
    with db.session.begin(subtransactions=True):
        task.switch_completion_of_task()
    db.session.commit()
    return redirect(url_for('todo.home'))

@todo.route('/uncomplete_task/<int:id>')
@login_required
def uncomplete_task(id):
    task = Task.query.get(id)
    if not task.user_id == int(current_user.get_id()):
        return redirect(url_for('todo.completed_tasks'))
    with db.session.begin(subtransactions=True):
        task.switch_completion_of_task()
    db.session.commit()
    return redirect(url_for('todo.completed_tasks'))

@todo.route('/percent_complete_ajax', methods=['POST'])
def percent_complete_ajax():
    if request.method == 'POST':
        percent_complete_of_task = request.form.to_dict()
        task_id = next(iter(percent_complete_of_task))
        task = Task.query.get(task_id)
        if not task.user_id == int(current_user.get_id()):
            return redirect(url_for('todo.home'))
        with db.session.begin(subtransactions=True):
            task.percent_complete = percent_complete_of_task[task_id]
            task.update_at = datetime.now(pytz.timezone('Asia/Tokyo'))
        db.session.commit()
    return jsonify(success=True, data=None)


@todo.route('/completed_tasks')
@login_required
def completed_tasks():
    user_id = current_user.get_id()
    tasks = Task.select_completed_tasks_by_user_id(user_id)
    return render_template('todo/completed_tasks.html', tasks=tasks)


@todo.route('/user', methods=['GET', 'POST'])
@login_required
def user():
    form = UserForm(request.form)
    if request.method == 'POST' and form.validate():
        user_id = current_user.get_id()
        user = User.select_user_by_id(user_id)
        with db.session.begin(subtransactions=True):
            user.username = form.username.data
            user.email = form.email.data
            user.update_at = datetime.now(pytz.timezone('Asia/Tokyo'))
        db.session.commit()
        flash('登録情報を更新しました')
    return render_template('todo/user.html', form=form)

@todo.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm(request.form)
    if request.method == 'POST' and form.validate():
        user_id = current_user.get_id()
        user = User.select_user_by_id(user_id)
        new_password = form.new_password.data
        with db.session.begin(subtransactions=True):
            user.save_new_password(new_password)
        db.session.commit()
        flash('パスワードを変更しました')
    return render_template('todo/change_password.html', form=form)

@todo.route('/delete_user', methods=['GET', 'POST'])
@login_required
def delete_user():
    form = DeleteUserForm(request.form)
    if request.method == 'POST' and form.validate():
        user_id = current_user.get_id()
        user = User.select_user_by_id(user_id)
        with db.session.begin(subtransactions=True):
            user.is_active = False
            user.update_at = datetime.now(pytz.timezone('Asia/Tokyo'))
        db.session.commit()
        flash('退会処理が完了しました。')
        logout_user()
        return redirect(url_for('todo.goodbye'))
    return render_template('todo/delete_user.html', form=form)

@todo.route('/goodbye')
def goodbye():
    return render_template('todo/goodbye.html')


@todo.route('/privacy')
def privacy():
    return render_template('todo/privacy.html')

@todo.route('/terms')
def terms():
    return render_template('todo/terms.html')


@todo.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm(request.form)
    if request.method == 'POST' and form.validate():
        contact = Contact(
            name = form.name.data,
            email = form.email.data,
            message = form.message.data
        )
        with db.session.begin(subtransactions=True):
            contact.create_new_contact()
        db.session.commit()
        recipient = 'multitasker.application@gmail.com'
        message_of_mail = MessageOfMail('お問い合わせが届きました', recipients=[recipient])
        message_of_mail.html = ('<p><b>以下の方からお問い合わせです！</b><p>'
                                '<p>氏名：' + contact.name + '</p>'
                                '<p>アドレス：' + contact.email + '</p>'
                                '<p>お問い合わせ内容：' + contact.message + '</p>')
        mail.send(message_of_mail)
        return redirect(url_for('todo.thankyou'))
    return render_template('todo/contact.html', form=form)

@todo.route('/thankyou')
def thankyou():
    return render_template('todo/thankyou.html')


@todo.app_errorhandler(404)
def page_not_found(e):
    return render_template('todo/404.html'), 404

@todo.app_errorhandler(500)
def server_error(e):
    return render_template('todo/500.html'), 500