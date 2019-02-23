from app import app, db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

interests_table = db.Table('interests_user',
                           db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                           db.Column('interest_id', db.Integer, db.ForeignKey('interests.id'))
                           )
meta_tags_table = db.Table('tags_channel',
                           db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                           db.Column('meta_tags_id', db.Integer, db.ForeignKey('meta_tags.id'))
                           )


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    channel_name = db.Column(db.String(100))
    avatar = db.Column(db.LargeBinary)
    email = db.Column(db.String(120), unique=True)
    birthday = db.Column(db.DateTime)
    interests = db.relationship('Interests', secondary=interests_table, backref=db.backref('users', lazy='dynamic'))
    about_channel = db.Column(db.Text(3000))
    meta_tags = db.relationship('MetaTags', secondary=meta_tags_table, backref=db.backref('users', lazy='dynamic'))
    password_hash = db.Column(db.String(120))

    def __repr__(self):
        return '<User {}, channel_name {}>'.format(self.username, self.channel_name)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Interests(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(120), unique=True)

    def __repr__(self):
        return '<Interest {}>'.format(self.text)


class MetaTags(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(120), unique=True)

    def __repr__(self):
        return '<MetaTag {}>'.format(self.text)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
