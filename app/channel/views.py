from . import channel
from app.models import User
from flask import render_template, flash, redirect, url_for, request
from app.views import correct_form_views
from app import db
from datetime import datetime
from .forms import ChannelHeadForm
from flask_login import current_user
from werkzeug.urls import url_parse


# Подписаться на канал
@channel.route('/subscribe/<username>')
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
@channel.route('/unsubscribe/<username>')
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


@channel.route('/<int:user_id>/main', methods=['GET', 'POST'])
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
        return redirect(url_for('channel.channel_main', user_id=user_id))
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

    return render_template('channel/channel_main.html', title=user.channel_name + ' - Ordis', user=user, is_channel_head=is_channel_head, form=form,
                           channel_name=channel_name,
                           lessons=lessons[:5], views=views_name, dates=dates)


@channel.route('/<int:user_id>/lessons', methods=['GET', 'POST'])
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
        return redirect(url_for('channel.channel_main', user_id=user_id))
    lessons = user.lessons
    lessons = list(reversed(sorted(lessons, key=lambda x: x.date_added)))
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

    return render_template('channel/channel_lessons.html', title=user.channel_name + ' - Ordis', user=user, is_channel_head=is_channel_head, form=form,
                           channel_name=channel_name,
                           lessons=lessons, views=views_name, dates=dates)
