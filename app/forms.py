from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FileField, DateField, TextAreaField, MultipleFileField
from wtforms.validators import DataRequired, Email, EqualTo, Optional, ValidationError
from app.models import User


class LoginForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class RegistrationForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    channel_name = StringField('Название канала', validators=[DataRequired()])
    avatar = FileField('Выберите аватар(50x50)', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    birthday = DateField('Дата рождения', format='%d.%m.%Y', validators=[Optional()])
    interests = StringField('Интересы', validators=[DataRequired()])
    about_channel = TextAreaField('Описание канала', validators=[DataRequired()])
    meta_tags = StringField('Мета-теги', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    repeat_password = PasswordField('Повторите пароль', validators=[EqualTo('password')])
    agree = BooleanField('Я согласен(-на) с')
    submit = SubmitField('Зарегистрироваться')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Такой пользователь уже зарегистрирован.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Такой e-mail адресс уже используется.')

    def validate_agree(self, value):
        if not value.data:
            raise ValidationError('Необходимо ваше согласие для регистрации.')


class AddLessonForm(FlaskForm):
    lesson_name = StringField('Название урока', validators=[DataRequired()])
    preview = FileField('Превью урока', validators=[DataRequired()], render_kw={'accept': 'image/*'})
    video = FileField('Видео', validators=[DataRequired()], render_kw={'accept': 'video/*'})
    about_lesson = TextAreaField('Описание урока', validators=[DataRequired()])
    attached_file = MultipleFileField('Вложенные файлы')
    extra_material = TextAreaField('Дополнительный материал', validators=[DataRequired()])
    meta_tags = StringField('Мета-теги', validators=[DataRequired()])
    submit = SubmitField('Добавить урок')


class ChannelHeadForm(FlaskForm):
    image = FileField('Картинка', render_kw={'accept': 'image/*'})
    submit = SubmitField('Изменить оформление канала')
