from app import app, db
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from app.forms import LoginForm, RegistrationForm
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


@app.route('/sign-in', methods=['GET', 'POST'])
def sign_in():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    print('ОК')
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None:
            flash('Пользователь с таким именем уже существует.')
        else:
            file = request.files['avatar'].read()
            user = User(username=form.username.data, channel_name=form.channel_name.data,
                        avatar=file, email=form.email.data, birthday=form.birthday.data,
                        about_channel=form.about_channel.data)
            user.set_password(form.password.data)
            interest = form.interests.data.split(',')

            # Проверка, есть ли данный интерес в базе данных
            for i in range(len(interest)):
                interest[i] = interest[i].lower().rstrip().lstrip()
                if Interests.query.filter_by(text=interest[i]).first() is None:
                    intt = Interests(text=interest[i])
                    db.session.add(intt)
                    db.session.commit()
                user.interests.append(Interests.query.filter_by(text=interest[i]).first())
            meta_tags = form.meta_tags.data.split(',')

            # Проверка, есть ли данный мета-тег в базе данных
            for i in range(len(meta_tags)):
                meta_tags[i] = meta_tags[i].lower().rstrip().lstrip()
                if MetaTags.query.filter_by(text=meta_tags[i]).first() is None:
                    meta_tag = Interests(text=meta_tags[i])
                    db.session.add(meta_tag)
                    db.session.commit()
                user.meta_tags.append(MetaTags.query.filter_by(text=interest[i]).first())

            db.session.add(user)
            db.session.commit()
            user = User.query.filter_by(username=form.username.data).first()
            login_user(user)
            return redirect(url_for('index'))
    return render_template('register.html', form=form, title='Регистрация')


@app.route('/logout')
def logout():
    logout_user()  # Разлогиниваем пользователя
    return redirect(url_for('index'))
