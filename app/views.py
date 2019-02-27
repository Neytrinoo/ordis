from app import app, db
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from app.forms import LoginForm, RegistrationForm, AddLessonForm
from app.models import User, Interests, MetaTags
from werkzeug.urls import url_parse


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Неверное имя пользователя или пароль')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/user-argeement')
def user_agreement():
    return render_template('user_agreement.html', title='Ordis - Пользовательское соглашение')


@app.route('/user/<int:id>/avatar')
def avatar(id):
    avatar = User.query.filter_by(id=id).first().avatar
    return app.response_class(avatar, mimetype='application/octet-stream')


@app.route('/add_lesson', methods=['GET', 'POST'])
@login_required
def add_lesson():
    form = AddLessonForm()
    if form.validate_on_submit():
        file = request.files.getlist('attached_file')
        print(file[1].read())
    return render_template('add_lesson.html', form=form, title='Ordis - Добавление урока')


@app.route('/sign-in', methods=['GET', 'POST'])
def sign_in():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        file = request.files['avatar'].read()
        user = User(username=form.username.data, channel_name=form.channel_name.data,
                    avatar=file, email=form.email.data, birthday=form.birthday.data,
                    about_channel=form.about_channel.data)
        user.set_password(form.password.data)
        interest = form.interests.data.split(',')
        meta_tags = form.meta_tags.data.split(',')

        # Проверка, есть ли данный интерес в базе данных
        for i in range(len(interest)):
            interest[i] = interest[i].lower().rstrip().lstrip()
            if Interests.query.filter_by(text=interest[i]).first() is None:
                db.session.add(Interests(text=interest[i]))
            if Interests.query.filter_by(text=interest[i]).first() not in user.interests:
                user.interests.append(Interests.query.filter_by(text=interest[i]).first())
            db.session.commit()

        # Проверка, есть ли данный мета-тег в базе данных
        for i in range(len(meta_tags)):
            meta_tags[i] = meta_tags[i].lower().rstrip().lstrip()
            if MetaTags.query.filter_by(text=meta_tags[i]).first() is None:
                db.session.add(MetaTags(text=meta_tags[i]))
            if MetaTags.query.filter_by(text=interest[i]).first() not in user.meta_tags:
                user.meta_tags.append(MetaTags.query.filter_by(text=interest[i]).first())
            db.session.commit()

        db.session.add(user)
        db.session.commit()
        user = User.query.filter_by(username=form.username.data).first()
        login_user(user)
        return redirect(url_for('index'))

    return render_template('register.html', form=form, title='Ordis - Регистрация')


@app.route('/logout')
def logout():
    logout_user()  # Разлогиниваем пользователя
    return redirect(url_for('index'))
