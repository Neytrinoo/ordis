from app import app, db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime

interests_table = db.Table('interests_user',
                           db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                           db.Column('interest_id', db.Integer, db.ForeignKey('interests.id'))
                           )
meta_tags_table = db.Table('tags_channel',
                           db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                           db.Column('meta_tags_id', db.Integer, db.ForeignKey('meta_tags.id'))
                           )

meta_tags_lesson_table = db.Table('tags_lesson',
                                  db.Column('lesson_id', db.Integer, db.ForeignKey('single_lesson.id')),
                                  db.Column('meta_tag_lesson_id', db.Integer, db.ForeignKey('meta_tags_lesson.id'))
                                  )
subscribers_channel = db.Table('subscribers_channel',
                               db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
                               db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
                               )


# Таблица пользователя
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    channel_name = db.Column(db.String(200))
    avatar = db.Column(db.LargeBinary)
    email = db.Column(db.String(200), unique=True)
    birthday = db.Column(db.DateTime)
    interests = db.relationship('Interests', secondary=interests_table, backref=db.backref('users', lazy='dynamic'))
    about_channel = db.Column(db.Text(3000))
    meta_tags = db.relationship('MetaTags', secondary=meta_tags_table, backref=db.backref('users', lazy='dynamic'))
    password_hash = db.Column(db.String(400))
    channel_head = db.Column(db.LargeBinary)
    # Самореферентное отношение между базой данных пользователей для реализации подписки
    followed = db.relationship('User', secondary=subscribers_channel, primaryjoin=(subscribers_channel.c.follower_id == id),
                               secondaryjoin=(subscribers_channel.c.followed_id == id),
                               backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

    def __repr__(self):
        return '<User {}, channel_name {}>'.format(self.username, self.channel_name)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(subscribers_channel.c.followed_id == user.id).count() > 0
    # Мета-теги для урока


class MetaTagsLesson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(600), nullable=False)


# Вложенные файлы для урока
class AttachedFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_path = db.Column(db.String(400))
    lesson_id = db.Column(db.Integer, db.ForeignKey('single_lesson.id'))  # Связь один-ко-многим с таблицей SingleLesson
    lesson = db.relationship('SingleLesson', backref=db.backref('attached_files', lazy=True))
    filename = db.Column(db.String(120))


# Видео в уроке
class VideoLesson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_path = db.Column(db.String(400))
    duration = db.Column(db.String(10))


# Одиночный урок, который не входит в курс
class SingleLesson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lesson_name = db.Column(db.String(256))
    preview = db.Column(db.LargeBinary, nullable=False)
    video_id = db.Column(db.Integer, db.ForeignKey('video_lesson.id'))
    video = db.relationship('VideoLesson', backref=db.backref('lesson', uselist=False))  # Связь один-к-одному с таблицей VideoLesson
    about_lesson = db.Column(db.String(3000))
    extra_material = db.Column(db.String(20000))
    views = db.Column(db.Integer, default=0)
    meta_tags = db.relationship('MetaTagsLesson', secondary=meta_tags_lesson_table, backref=db.backref('lesson', lazy='dynamic'))  # Связь многие-ко-многим с таблицей
    # MetaTagsLesson
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # Связь один-ко-многим с таблицей User
    user = db.relationship('User', backref=db.backref('lessons', lazy=True))
    archive_attached_files_path = db.Column(db.String(400))
    date_added = db.Column(db.DateTime, default=datetime.utcnow)


# Интересы пользователя
class Interests(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(256))

    def __repr__(self):
        return '<Interest {}>'.format(self.text)


# Мета-теги для канала пользователя
class MetaTags(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(256))

    def __repr__(self):
        return '<MetaTag {}>'.format(self.text)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
