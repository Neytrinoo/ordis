from app import app, db
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from app.forms import LoginForm, RegistrationForm, AddLessonForm,  CommentLessonForm, SearchForm
from app.models import User, Interests, MetaTags, SingleLesson, VideoLesson, AttachedFile, MetaTagsLesson, LessonComment
from werkzeug.urls import url_parse
from moviepy.editor import VideoFileClip
from datetime import datetime
from zipfile import ZipFile
from os.path import join, dirname, realpath
import pymorphy2
from random import randint

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
    if current_user.is_authenticated:
        interests = current_user.interests
        lesson_tags = {}
        for interest in interests:
            if MetaTagsLesson.query.filter_by(text=interest.text).first() is not None:
                for lesson in MetaTagsLesson.query.filter_by(text=interest.text).first().lesson:
                    if lesson in lesson_tags:
                        lesson_tags[lesson] += 1
                    else:
                        lesson_tags[lesson] = 1
        lesson_tags = list(reversed(sorted(lesson_tags.items(), key=lambda x: x[1])))
        views_name = []
        dates = []
        for lesson, les_count in lesson_tags:
            res = correct_form_views(lesson.views)
            views_name.append(res)
            now = datetime.utcnow()
            if lesson.date_added.day == now.day:
                date = lesson.date_added.strftime('%H:%M')
            else:
                date = lesson.date_added.strftime('%d.%m.%Y')
            dates.append(date)
        lesson_tags = [x[0] for x in lesson_tags[:10]]
    else:
        a = len(SingleLesson.query.all())
        lesson_tags = []
        views_name = []
        dates = []
        while len(lesson_tags) < 10:
            lesson = SingleLesson.query.filter_by(id=randint(1, a)).first()
            if lesson is not None and lesson not in lesson_tags:
                lesson_tags.append(lesson)
                res = correct_form_views(lesson.views)
                views_name.append(res)
                now = datetime.utcnow()
                if lesson.date_added.day == now.day:
                    date = lesson.date_added.strftime('%H:%M')
                else:
                    date = lesson.date_added.strftime('%d.%m.%Y')
                dates.append(date)
            if a == len(lesson_tags):
                break

    return render_template('index.html', lessons=lesson_tags, views=views_name, dates=dates)


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
        clip.reader.close()
        clip.audio.reader.close_proc()

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


# Функция поиска
@app.route('/search')
def search():
    morph = pymorphy2.MorphAnalyzer()
    search_text = request.args.get('search_input')
    copy_search_text = search_text
    what_is = request.args.get('what_is')
    if not search_text or url_parse(search_text).netloc != '':
        flash('Поисковый запрос пуст')
        return redirect(url_for('index'))

    search_text = search_text.split()
    need_tags = []
    lesson_tags = []
    for line in search_text:
        search_now = morph.parse(line.lower())[0].normal_form
        if MetaTags.query.filter_by(text=search_now).first() is not None:
            need_tags.append(MetaTags.query.filter_by(text=search_now).first())
        if MetaTagsLesson.query.filter_by(text=search_now).first() is not None:
            lesson_tags.append(MetaTagsLesson.query.filter_by(text=search_now).first())

    users_tags = {}
    lesson_tags_count = {}
    if what_is == 'lessons' or what_is is None:
        for tag in lesson_tags:
            for lesson in tag.lesson:
                if lesson not in lesson_tags_count:
                    lesson_tags_count[lesson] = 1
                else:
                    lesson_tags_count[lesson] += 1
        lesson_tags_count = list(reversed(sorted(lesson_tags_count.items(), key=lambda x: x[1])))

        if not lesson_tags_count:
            flash('Ничего не найдено')
            return redirect(url_for('index'))
        views_name = []
        dates = []
        for lesson, les_id in lesson_tags_count:
            res = correct_form_views(lesson.views)
            views_name.append(res)
            now = datetime.utcnow()
            if lesson.date_added.day == now.day:
                date = lesson.date_added.strftime('%H:%M')
            else:
                date = lesson.date_added.strftime('%d.%m.%Y')
            dates.append(date)

        return render_template('search_lesson.html', lessons=[x[0] for x in lesson_tags_count], views=views_name, dates=dates, search=copy_search_text)
    for tag in need_tags:
        for user in tag.users:
            if user not in users_tags:
                users_tags[user] = 1
            else:
                users_tags[user] += 1
    users_tags = list(reversed(sorted(users_tags.items(), key=lambda x: x[1])))
    print(users_tags)
    return render_template('search_users.html', users=[x[0] for x in users_tags], search=copy_search_text)


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
        comment = LessonComment(text=text, rating=stars)
        change_rating = True
        for comment2 in current_user.comments:
            if comment2.lesson_id == lesson_id:
                change_rating = False
        # Общий рейтинг урока изменяется только в том случае, если данный пользователь оставил свой первый комментарий
        if change_rating:
            lesson.rating_sum += stars
            lesson.rating_influence_comments += 1
            lesson.rating = lesson.rating_sum / lesson.rating_influence_comments
            comment.rating_influence = True
        else:
            comment.rating_influence = False
        lesson.comments.append(comment)
        current_user.comments.append(comment)
        db.session.add(comment)
        db.session.commit()
        return redirect(url_for('lesson_page', lesson_id=lesson.id))
    count_comments = len(lesson.comments)
    return render_template('lesson_page.html', title=lesson.lesson_name + ' - Ordis', lesson=lesson, views=views, filenames=filenames, form=form,
                           count_comments=count_comments)


# Регистрация
@app.route('/sign-in', methods=['GET', 'POST'])
def sign_in():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        if form.avatar.data:
            file = request.files['avatar'].read()
        else:
            file = open(join(dirname(realpath(__file__)), 'static/img/user_default_avatar.png'), 'rb').read()

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
