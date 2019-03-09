from app import app, db
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from app.forms import LoginForm, RegistrationForm, AddLessonForm, ChannelHeadForm, CommentLessonForm
from app.models import User, Interests, MetaTags, SingleLesson, VideoLesson, AttachedFile, MetaTagsLesson, LessonComment
from werkzeug.urls import url_parse
from moviepy.editor import VideoFileClip
from datetime import datetime
from zipfile import ZipFile
from os.path import join, dirname, realpath

VIEWS = {
    '1': 'просмотр',
    '2': 'просмотра',
    '3': 'просмотра',
    '4': 'просмотра',
    '5': 'просмотров',
    '6': 'просмотров',
    '7': 'просмотров',
    '8': 'просмотров',
    '9': 'просмотров',
    '0': 'просмотров',
    '11': 'просмотров',
    '12': 'просмотров',
    '13': 'просмотров',
    '14': 'просмотров',
}


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


# Возвращает аватар
@app.route('/user/<int:id>/avatar')
def avatar(id):
    avatar = User.query.filter_by(id=id).first().avatar
    return app.response_class(avatar, mimetype='application/octet-stream')


# Возвращает картинку превью урока
@app.route('/lesson/<int:id>/preview')
def lesson_preview(id):
    preview = SingleLesson.query.filter_by(id=id).first().preview
    return app.response_class(preview, mimetype='application/octet-stream')


# Возвращает картинку шапки канала из базы данных
@app.route('/user/<int:user_id>/channel_head')
def channel_head(user_id):
    channel_head = User.query.filter_by(id=user_id).first().channel_head
    return app.response_class(channel_head, mimetype='application/octet-stream')


# Добавление урока
@app.route('/add_lesson', methods=['GET', 'POST'])
@login_required
def add_lesson():
    form = AddLessonForm()
    if form.validate_on_submit():
        # file = request.files.getlist('attached_file')
        video = request.files['video']
        preview = request.files['preview'].read()
        # Путь до видео урока в файловой системе. Создается так: data/videos/имяПользователя_КоличествоУроковУПользователя+1.расширениеФайла
        video_path = 'data/videos/' + current_user.username + '_' + str(len(current_user.lessons) + 1) + '.' + video.filename.split('.')[-1]
        video.save('app/static/' + video_path)
        clip = VideoFileClip('app/static/' + video_path)
        duration = int(clip.duration)
        res = ''
        m = duration // 60
        if m > 0:
            duration -= m * 60
        h = duration // 3600
        if h > 0:
            duration -= h * 3600
        res = '0' * (2 - len(str(m))) + str(m) + ':' + '0' * (2 - len(str(duration))) + str(duration)
        if h > 0:
            res = '0' * (2 - len(str(h))) + str(h) + ':' + res
        video = VideoLesson(file_path=video_path, duration=res)
        lesson = SingleLesson(lesson_name=form.lesson_name.data, preview=preview, about_lesson=form.about_lesson.data, extra_material=form.extra_material.data,
                              video=video)

        # Форматируем и добавляем мета-теги
        meta_tags = form.meta_tags.data.split(',')
        for i in range(len(meta_tags)):
            meta_tags[i] = meta_tags[i].lower().rstrip().lstrip()
            if len(meta_tags[i]) >= 600:
                continue
            if MetaTagsLesson.query.filter_by(text=meta_tags[i]).first() is None:
                db.session.add(MetaTagsLesson(text=meta_tags[i]))
            if MetaTagsLesson.query.filter_by(text=meta_tags[i]).first() not in lesson.meta_tags:
                lesson.meta_tags.append(MetaTagsLesson.query.filter_by(text=meta_tags[i]).first())
            db.session.commit()

        # Добавляем вложенные файлы
        attached_files = request.files.getlist('attached_file')
        myzip = ZipFile(join(dirname(realpath(__file__)), 'static/data/attached_files_archives/' + current_user.username + '_' + str(lesson.id) + '.zip'), 'w')
        for i in range(len(attached_files)):
            # Путь до вложенного файла в файловой системе. Создается так: data/attached_files/имяПользователя_idУрока_КоличествоВложенныхФайловВУроке+1.расширениеФайла
            file_path = 'data/attached_files/' + current_user.username + '_' + str(lesson.id) + '_' + str(len(lesson.attached_files) + 1) + '.' + \
                        attached_files[i].filename.split('.')[-1]
            attached_files[i].save('app/static/' + file_path)
            if len(attached_files[i].filename) >= 119:
                file = AttachedFile(file_path=file_path, filename='attached_files' + attached_files[i].filename.split('.')[-1])
            else:
                file = AttachedFile(file_path=file_path, filename=attached_files[i].filename)
            myzip.write(join(dirname(realpath(__file__)), 'static/' + file_path), arcname=attached_files[i].filename)
            lesson.archive_attached_files_path = 'data/attached_files_archives/' + current_user.username + '_' + str(lesson.id) + '.zip'
            lesson.attached_files.append(file)
            db.session.add(file)
            db.session.commit()

        current_user.lessons.append(lesson)
        db.session.add(lesson)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('add_lesson.html', form=form, title='Ordis - Добавление урока')


# Подписаться на канал
@app.route('/subscribe/<username>')
def subscribe(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Пользователь {} не найден'.format(username))
        return redirect(url_for('index'))
    if current_user.is_anonymous:
        return redirect(url_for('sign_in'))
    current_user.follow(user)
    db.session.commit()
    next_page = request.args.get('next')
    if not next_page or url_parse(next_page).netloc != '':
        next_page = url_for('channel_main', user_id=user.id)
    return redirect(next_page)


# Отписаться от канала
@app.route('/unsubscribe/<username>')
def unsubscribe(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Пользователь {} не найден'.format(username))
        return redirect(url_for('index'))
    if current_user.is_anonymous:
        return redirect(url_for('sign_in'))
    current_user.unfollow(user)
    db.session.commit()
    next_page = request.args.get('next')
    if not next_page or url_parse(next_page).netloc != '':
        next_page = url_for('channel_main', user_id=user.id)
    return redirect(next_page)


def correct_form_views(view):
    view = str(view)
    if view in VIEWS:
        res = VIEWS[view]
    elif len(view) >= 2 and view[-2:] in VIEWS:
        res = VIEWS[view[-2:]]
    else:
        res = VIEWS[view[-1]]
    return res


# Страница канала
@app.route('/channel/<int:user_id>/main', methods=['GET', 'POST'])
def channel_main(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        flash('Такого канала не существует')
        return redirect(url_for('index'))
    is_channel_head = True
    if user.channel_head is None:
        print(user.channel_head)
        is_channel_head = False
    form = ChannelHeadForm()
    channel_name = user.channel_name
    # Обработка изменения шапки канала
    if form.validate_on_submit():
        if form.image.data:
            file = request.files['image'].read()
            user.channel_head = file
            db.session.commit()
        return redirect(url_for('channel_main', user_id=user_id))
    lessons = user.lessons
    lessons = list(reversed(sorted(lessons, key=lambda x: x.views)))
    views_name = []
    dates = []
    # Добавляем в views_name правильное склонение числа просмотров, а в dates - правильное отображение даты.
    # Если урок добавлен в нынешний день, то время, если нет - то дата
    for lesson in lessons:
        res = correct_form_views(lesson.views)
        views_name.append(res)
        now = datetime.utcnow()
        if lesson.date_added.day == now.day:
            date = lesson.date_added.strftime('%H:%M')
        else:
            date = lesson.date_added.strftime('%d.%m.%Y')
        dates.append(date)

    return render_template('channel_main.html', title=user.channel_name + ' - Ordis', user=user, is_channel_head=is_channel_head, form=form, channel_name=channel_name,
                           lessons=lessons[:5], views=views_name, dates=dates)


@app.route('/channel/<int:user_id>/lessons', methods=['GET', 'POST'])
def channel_lessons(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        flash('Такого канала не существует')
        return redirect(url_for('index'))
    is_channel_head = True
    if user.channel_head is None:
        print(user.channel_head)
        is_channel_head = False
    form = ChannelHeadForm()
    channel_name = user.channel_name
    # Обработка изменения шапки канала
    if form.validate_on_submit():
        if form.image.data:
            file = request.files['image'].read()
            user.channel_head = file
            db.session.commit()
        return redirect(url_for('channel_main', user_id=user_id))
    lessons = user.lessons
    lessons = list(reversed(sorted(lessons, key=lambda x: x.views)))
    views_name = []
    dates = []
    # Добавляем в views_name правильное склонение числа просмотров, а в dates - правильное отображение даты.
    # Если урок добавлен в нынешний день, то время, если нет - то дата
    for lesson in lessons:
        res = correct_form_views(lesson.views)
        views_name.append(res)
        now = datetime.utcnow()
        if lesson.date_added.day == now.day:
            date = lesson.date_added.strftime('%H:%M')
        else:
            date = lesson.date_added.strftime('%d.%m.%Y')
        dates.append(date)

    return render_template('channel_lessons.html', title=user.channel_name + ' - Ordis', user=user, is_channel_head=is_channel_head, form=form, channel_name=channel_name,
                           lessons=lessons, views=views_name, dates=dates)


# Страница урока
@app.route('/lesson/<int:lesson_id>', methods=['GET', 'POST'])
def lesson_page(lesson_id):
    lesson = SingleLesson.query.filter_by(id=lesson_id).first()
    if lesson is None:
        flash('Такого урока нет!')
        return redirect(url_for('index'))
    lesson.views += 1
    db.session.commit()
    views = correct_form_views(lesson.views)
    filenames = ', '.join([file.filename for file in lesson.attached_files])
    form = CommentLessonForm()
    if form.validate_on_submit():
        text = form.comment.data
        stars = int(form.stars.data)
        lesson.rating_sum += stars
        comment = LessonComment(text=text, rating=stars)
        lesson.rating = lesson.rating_sum / (len(lesson.comments) + 1)
        lesson.comments.append(comment)
        current_user.comments.append(comment)
        db.session.commit()
        return redirect(url_for('lesson_page', lesson_id=lesson.id))
    count_comments = len(lesson.comments)
    print(lesson.rating)
    return render_template('lesson_page.html', title=lesson.lesson_name + ' - Ordis', lesson=lesson, views=views, filenames=filenames, form=form,
                           count_comments=count_comments)


# Регистрация
@app.route('/sign-in', methods=['GET', 'POST'])
def sign_in():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
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
            if len(interest[i]) >= 256:
                continue
            if Interests.query.filter_by(text=interest[i]).first() is None:
                db.session.add(Interests(text=interest[i]))
            if Interests.query.filter_by(text=interest[i]).first() not in user.interests:
                user.interests.append(Interests.query.filter_by(text=interest[i]).first())
            db.session.commit()

        # Проверка, есть ли данный мета-тег в базе данных
        for i in range(len(meta_tags)):
            meta_tags[i] = meta_tags[i].lower().rstrip().lstrip()
            if len(meta_tags[i]) >= 256:
                continue
            if MetaTags.query.filter_by(text=meta_tags[i]).first() is None:
                db.session.add(MetaTags(text=meta_tags[i]))
            if MetaTags.query.filter_by(text=meta_tags[i]).first() not in user.meta_tags:
                user.meta_tags.append(MetaTags.query.filter_by(text=meta_tags[i]).first())
            db.session.commit()

        db.session.add(user)
        db.session.commit()
        user = User.query.filter_by(username=form.username.data).first()
        login_user(user)
        return redirect(url_for('index'))

    return render_template('register.html', form=form, title='Ordis - Регистрация')


@app.route('/logout')
@login_required
def logout():
    logout_user()  # Разлогиниваем пользователя
    return redirect(url_for('index'))
