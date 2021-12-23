from flask_login import current_user
from flask_wtf import FlaskForm

from wtforms import ValidationError
from wtforms.fields import StringField, PasswordField, DateField, RadioField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from wtforms.widgets.core import TextArea

from flask_app.models import User


def validate_password_min(self, field):
    if len(field.data) < 8:
        raise ValidationError('パスワードは8文字以上にしてください')


class RegisterForm(FlaskForm):
    username = StringField('ニックネーム', validators=[DataRequired('入力が必要です'), Length(0, 64, '64文字以内です')])
    email = StringField('メールアドレス', validators=[DataRequired('入力が必要です'), Email('有効な形のメールアドレスではありません'), Length(0, 64, '64文字以内です')])
    password = PasswordField('パスワード（8文字以上）', validators=[DataRequired('入力が必要です'), EqualTo('confirm_password', message='再入力のパスワードと一致しません'), validate_password_min, Length(0, 128, '128文字以内です')])
    confirm_password = PasswordField('パスワード確認（再入力）', validators=[DataRequired('入力が必要です')])
    submit = SubmitField('同意して新規登録')

    def validate_email(self, field):
        if User.select_user_by_email(field.data):
            raise ValidationError('そのメールアドレスは使用できません')


class LoginForm(FlaskForm):
    email = StringField('メールアドレス', validators=[DataRequired('入力が必要です')])
    password = PasswordField('パスワード', validators=[DataRequired('入力が必要です')])
    submit = SubmitField('ログイン')


class UserForm(FlaskForm):
    username = StringField('ニックネーム', validators=[DataRequired('入力が必要です'), Length(0, 64, '64文字以内です')])
    email = StringField('メールアドレス', validators=[DataRequired('入力が必要です'), Email('有効な形のメールアドレスではありません'), Length(0, 64, '64文字以内です')])
    submit = SubmitField('登録情報更新')

    def validate_email(self, field):
        user = User.select_user_by_email(field.data)
        if user.id != int(current_user.get_id()):
            raise ValidationError('そのメールアドレスは使用できません')


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('現在のパスワード', validators=[DataRequired('入力が必要です')])
    new_password = PasswordField('新しいパスワード（8文字以上）', validators=[DataRequired('入力が必要です'), EqualTo('confirm_password', message='再入力のパスワードと一致しません'), validate_password_min, Length(0, 128, '128文字以内です')])
    confirm_password = PasswordField('新しいパスワード（再入力）', validators=[DataRequired('入力が必要です')])
    submit = SubmitField('パスワード変更')

    def validate_current_password(self, field):
        user_id = current_user.get_id()
        user = User.select_user_by_id(user_id)
        if not user.validate_password(field.data):
            raise ValidationError('パスワードが間違っています')


class DeleteUserForm(FlaskForm):
    current_password = PasswordField('現在のパスワード', validators=[DataRequired('入力が必要です')])
    submit = SubmitField('本当に退会する')

    def validate_current_password(self, field):
        user_id = current_user.get_id()
        user = User.select_user_by_id(user_id)
        if not user.validate_password(field.data):
            raise ValidationError('パスワードが間違っています')


class TaskForm(FlaskForm):
    taskname = StringField('タスク名', validators=[DataRequired('入力が必要です'), Length(0, 64, '64文字以内です')])
    description = StringField('タスク内容', widget=TextArea(), validators=[Length(0, 255, '255文字以内です')])
    due = DateField('期限', validators=[DataRequired('入力が必要です')])
    submit = SubmitField('')


class ContactForm(FlaskForm):
    name = StringField('お名前', validators=[DataRequired('入力が必要です'), Length(0, 64, '64文字以内です')])
    email = StringField('メールアドレス', validators=[DataRequired('入力が必要です'), Email('有効な形のメールアドレスではありません'), Length(0, 64, '64文字以内です')])
    message = StringField('お問い合わせ内容', widget=TextArea(), validators=[DataRequired('入力が必要です'), Length(0, 255, '255文字以内です')])
    submit = SubmitField('送信')


# 管理画面からロボットのメッセージを登録
class MessageForm(FlaskForm):
    message_type = RadioField('メッセージタイプ ', coerce=int, choices=[(1, '日付'), (2, '月'), (3, '時間帯'), (4, '役立ち情報'), (5, '励まし'), (6, '雑談')])
    date = StringField('日付', validators=[Length(0, 4, '4文字以内です')])
    month = RadioField('月', coerce=int, choices=[(1, '１月'), (2, '２月'), (3, '３月'), (4, '４月'), (5, '５月'), (6, '６月'), (7, '７月'), (8, '８月'), (9, '９月'), (10, '１０月'), (11, '１１月'), (12, '１２月'), (13, '無し')], default=13)
    time_period = RadioField('時間帯', coerce=int, choices=[(1, '深夜'), (2, '早朝'), (3, '朝'), (4, '午前'), (5, '昼'), (6, '午後'), (7, '夕方'), (8, '夜'), (9, '夜遅く'), (10, '無し')], default=10)
    message = StringField('メッセージ', widget=TextArea(), validators=[DataRequired('入力が必要です'), Length(0, 255, '255文字以内です')])
    submit = SubmitField('登録')