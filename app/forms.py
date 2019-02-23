from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FileField, DateField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Optional


class LoginForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class RegistrationForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    channel_name = StringField('Название канала', validators=[DataRequired()])
    avatar = FileField('Выберите аватар')
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    birthday = DateField('Дата рождения', format='%d/%m/%Y', validators=[Optional()])
    interests = StringField('Интересы')
    about_channel = TextAreaField('Описание канала')
    meta_tags = StringField('Мета-теги')
    password = PasswordField('Пароль', validators=[DataRequired()])
    repeat_password = PasswordField('Повторите пароль', validators=[EqualTo('password')])
    agree = BooleanField('Я согласен(-на) с пользовательским соглашением')
    submit = SubmitField('Зарегистрироваться')
