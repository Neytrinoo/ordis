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
            raise ValidationError('Такой пользователь уже зарегистрирован')
        if len(username.data) >= 100:
            raise ValidationError('Длина не должна превышать 100 символов')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Такой e-mail адресс уже используется.')
        if len(email.data) >= 200:
            raise ValidationError('Длина не должна превышать 200 символов')

    def validate_agree(self, value):
        if not value.data:
            raise ValidationError('Необходимо ваше согласие для регистрации.')

    def validate_channel_name(self, channel_name):
        if len(channel_name.data) >= 200:
            raise ValidationError('Длина не должна превышать 200 символов')

    def validate_about_channel(self, about_channel):
        if len(about_channel.data) >= 3000:
            raise ValidationError('Длина не должна превышать 3000 символов')

    def validate_password(self, password):
        if len(password.data) >= 120:
            raise ValidationError('Длина не должна превышать 120 символов')


class AddLessonForm(FlaskForm):
    lesson_name = StringField('Название урока', validators=[DataRequired()])
    preview = FileField('Превью урока', validators=[DataRequired()], render_kw={'accept': 'image/*'})
    video = FileField('Видео', validators=[DataRequired()], render_kw={'accept': 'video/*'})
    about_lesson = TextAreaField('Описание урока', validators=[DataRequired()])
    attached_file = MultipleFileField('Вложенные файлы')
    extra_material = TextAreaField('Дополнительный материал', validators=[DataRequired()])
    meta_tags = StringField('Мета-теги', validators=[DataRequired()])
    submit = SubmitField('Добавить урок')

    def validate_lesson_name(self, lesson_name):
        if len(lesson_name.data) >= 256:
            raise ValidationError('Длина не должна превышать 256 символов')

    def validate_about_lesson(self, about_lesson):
        if len(about_lesson.data) >= 3000:
            raise ValidationError('Длина не должна превышать 3000 символов')

    def validate_extra_material(self, extra_material):
        if len(extra_material.data) >= 20000:
            raise ValidationError('Длина не должна превышать 20000 символов')


class ChannelHeadForm(FlaskForm):
    image = FileField('Картинка', render_kw={'accept': 'image/*'})
    submit = SubmitField('Изменить оформление канала')
