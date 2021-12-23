import pytz
import random
from datetime import datetime, timedelta
from uuid import uuid4

from flask_bcrypt import check_password_hash, generate_password_hash
from flask_login import current_user, UserMixin

from sqlalchemy import desc

from flask_app import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class User(UserMixin, db.Model):

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True)
    email = db.Column(db.String(64), unique=True, index=True)
    password = db.Column(db.String(128))
    is_active = db.Column(db.Boolean, default=False)
    login_count = db.Column(db.Integer, default=0)
    create_tasks_count = db.Column(db.Integer, default=0)
    create_at = db.Column(db.DateTime, default=datetime.now(pytz.timezone('Asia/Tokyo')))
    update_at = db.Column(db.DateTime, default=datetime.now(pytz.timezone('Asia/Tokyo')))

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = generate_password_hash(password).decode('utf8')
        self.is_active = True
        self.create_at = datetime.now(pytz.timezone('Asia/Tokyo'))
        self.update_at = datetime.now(pytz.timezone('Asia/Tokyo'))

    @classmethod
    def select_all_users(cls):
        return cls.query.order_by(desc(cls.is_active)).all()

    @classmethod
    def select_user_by_id(cls, id):
        return cls.query.get(id)

    @classmethod
    def select_user_by_email(cls, email):
        return cls.query.filter_by(email=email).first()

    def create_new_user(self):
        db.session.add(self)
    
    def switch_activeness_of_user(self):
        if self.is_active == False:
            self.is_active = True
        else:
            self.is_active = False
        self.update_at = datetime.now(pytz.timezone('Asia/Tokyo'))

    def delete_user(self):
        db.session.delete(self)
        
    def validate_password(self, password):
        return check_password_hash(self.password, password)

    def save_new_password(self, new_password):
        self.password = generate_password_hash(new_password).decode('utf8')
        self.update_at = datetime.now(pytz.timezone('Asia/Tokyo'))


class PasswordResetToken(db.Model):

    __tablename__ = 'password_reset_tokens'

    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(64), unique=True, index=True, server_default=str(uuid4))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    expire_at = db.Column(db.DateTime, default=datetime.now(pytz.timezone('Asia/Tokyo')))
    create_at = db.Column(db.DateTime, default=datetime.now(pytz.timezone('Asia/Tokyo')))
    update_at = db.Column(db.DateTime, default=datetime.now(pytz.timezone('Asia/Tokyo')))

    def __init__(self, token, user_id, expire_at):
        self.token = token
        self.user_id = user_id
        self.expire_at = expire_at
        self.create_at = datetime.now(pytz.timezone('Asia/Tokyo'))
        self.update_at = datetime.now(pytz.timezone('Asia/Tokyo'))
    
    @classmethod
    def publish_token(cls, adminuser):
        token = str(uuid4())
        new_token = cls(
            token,
            adminuser.id,
            datetime.now(pytz.timezone('Asia/Tokyo')) + timedelta(days=1)
        )
        db.session.add(new_token)
        return token

    @classmethod
    def get_user_id_by_token(cls, token):
        now = datetime.now(pytz.timezone('Asia/Tokyo'))
        record = cls.query.filter_by(token=str(token)).filter(cls.expire_at > now).first()
        if record:
            return record.user_id
        else:
            return None
    
    @classmethod
    def delete_token(cls, token):
        cls.query.filter_by(token=str(token)).delete()


class Task(db.Model):

    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    taskname = db.Column(db.String(64), index=True)
    description = db.Column(db.String(255))
    due = db.Column(db.DateTime)
    percent_complete = db.Column(db.Integer, default=0)
    completed = db.Column(db.Boolean, default=False)
    create_at = db.Column(db.DateTime, default=datetime.now(pytz.timezone('Asia/Tokyo')))
    update_at = db.Column(db.DateTime, default=datetime.now(pytz.timezone('Asia/Tokyo')))

    def __init__(self, user_id, taskname, description, due):
        self.user_id = user_id
        self.taskname = taskname
        self.description = description
        self.due = due
        self.create_at = datetime.now(pytz.timezone('Asia/Tokyo'))
        self.update_at = datetime.now(pytz.timezone('Asia/Tokyo'))

    @classmethod
    def select_all_tasks_by_user_id(cls, user_id):
        return cls.query.filter_by(user_id = user_id).all()

    @classmethod
    def select_uncompleted_tasks_by_user_id(cls, user_id):
        datetime_now = datetime.now(pytz.timezone('Asia/Tokyo'))
        today = datetime_now.date()
        return cls.query.filter_by(
            user_id = user_id,
            completed = False
        ).order_by(cls.due).all()
    
    @classmethod
    def select_completed_tasks_by_user_id(cls, user_id):
        return cls.query.filter_by(
            user_id = user_id,
            completed = True
        ).order_by(cls.due).all()

    def create_new_task(self):
        db.session.add(self)
        current_user.create_tasks_count += 1
        current_user.update_at = datetime.now(pytz.timezone('Asia/Tokyo'))

    def delete_task(self):
        db.session.delete(self)

    def switch_completion_of_task(self):
        if self.completed == False:
            self.completed = True
        else:
            self.completed = False
        self.percent_complete = 0
        self.update_at = datetime.now(pytz.timezone('Asia/Tokyo'))


class Contact(db.Model):

    __tablename__ = 'contacts'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    email = db.Column(db.String(64), index=True)
    message = db.Column(db.String(255))
    completed = db.Column(db.Boolean, default=False)
    create_at = db.Column(db.DateTime, default=datetime.now(pytz.timezone('Asia/Tokyo')))
    update_at = db.Column(db.DateTime, default=datetime.now(pytz.timezone('Asia/Tokyo')))

    def __init__(self, name, email, message):
        self.name = name
        self.email = email
        self.message = message
        self.create_at = datetime.now(pytz.timezone('Asia/Tokyo'))
        self.update_at = datetime.now(pytz.timezone('Asia/Tokyo'))
    
    @classmethod
    def select_all_contacts(cls):
        return cls.query.order_by(cls.completed).all()
    
    def create_new_contact(self):
        db.session.add(self)
    
    def switch_completion_of_contact(self):
        if self.completed == False:
            self.completed = True
        else:
            self.completed = False
        self.update_at = datetime.now(pytz.timezone('Asia/Tokyo'))
    
    def delete_contact(self):
        db.session.delete(self)


# 管理画面からロボットのメッセージを登録
class Message(db.Model):

    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    message_type = db.Column(db.Integer, default=0, index=True)
    date = db.Column(db.String(4), default=None, index=True)
    month = db.Column(db.Integer, default=0, index=True)
    time_period = db.Column(db.Integer, default=0, index=True)
    message = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=False)
    create_at = db.Column(db.DateTime, default=datetime.now(pytz.timezone('Asia/Tokyo')))
    update_at = db.Column(db.DateTime, default=datetime.now(pytz.timezone('Asia/Tokyo')))

    def __init__(self, message_type, date, month, time_period, message):
        self.message_type = message_type
        self.date = date
        self.month = month
        self.time_period = time_period
        self.message = message
        self.is_active = True
        self.create_at = datetime.now(pytz.timezone('Asia/Tokyo'))
        self.update_at = datetime.now(pytz.timezone('Asia/Tokyo'))
    
    @classmethod
    def select_all_messages(cls):
        return cls.query.order_by(desc(cls.is_active), cls.message_type).all()

    @classmethod
    def select_message_by_message_type(cls, message_type, datetime_now):
        if current_user.login_count == 1 and current_user.create_tasks_count == 1:
            message = 'ようこそ、' + current_user.username + 'さん！ご登録ありがとうございます。\r\nチュートリアルにならい、タスクの作成から始めてみてください。'
            return message
        messages = []
        count = 0
        while not messages:
            count += 1
            if count == 5:
                break
            elif message_type == 1:
                date_of_now = str(datetime_now.month) + str(datetime_now.day)
                messages = cls.query.filter_by(date=date_of_now, is_active=True).all()
                message_type = random.randint(2, 6)
            elif message_type == 2:
                month_of_now = datetime_now.month
                messages = cls.query.filter_by(month=month_of_now, is_active=True).all()
            elif message_type == 3:
                hour_of_now = datetime_now.hour
                if 0 <= hour_of_now < 4:
                    time_period_of_now = 1
                elif 4 <= hour_of_now < 7:
                    time_period_of_now = 2
                elif 7 <= hour_of_now < 10:
                    time_period_of_now = 3
                elif 10 <= hour_of_now < 12:
                    time_period_of_now = 4
                elif 12 <= hour_of_now < 13:
                    time_period_of_now = 5
                elif 13 <= hour_of_now < 16:
                    time_period_of_now = 6
                elif 16 <= hour_of_now < 19:
                    time_period_of_now = 7
                elif 19 <= hour_of_now < 22:
                    time_period_of_now = 8
                elif 22 <= hour_of_now < 24:
                    time_period_of_now = 9
                else:
                    time_period_of_now = 0
                messages = cls.query.filter_by(time_period=time_period_of_now, is_active=True).all()
            else:
                messages = cls.query.filter_by(message_type=message_type, is_active=True).all()
        if len(messages) == 0:
            message = current_user.username + 'さん、お疲れ様です。\r\nやり切った自分へのご褒美を忘れないようにしましょう！'
            return message
        random_index = random.randint(0, len(messages)-1)
        message = messages[random_index]
        return message.message

    def create_new_message(self):
        db.session.add(self)
    
    def switch_activeness_of_message(self):
        if self.is_active == False:
            self.is_active = True
        else:
            self.is_active = False
        self.update_at = datetime.now(pytz.timezone('Asia/Tokyo'))
    
    def delete_message(self):
        db.session.delete(self)