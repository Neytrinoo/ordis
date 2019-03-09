from flask_restful import reqparse, abort, Api, Resource
from app import app, db
from app.models import User, SingleLesson, MetaTags, Interests
from flask import jsonify
import datetime

api = Api(app)


def abort_if_user_not_found(id):
    if User.query.filter_by(id=id).first() is None:
        abort(404, message="User {} not found".format(id))


class UserApi(Resource):
    def get(self, user_id):
        abort_if_user_not_found(user_id)
        user = User.query.filter_by(id=user_id).first()
        result = {
            'birthday': user.birthday,
            'username': user.username,
            'channel_name': user.channel_name,
            'meta-tags': str([text.text for text in user.meta_tags]),
            'subscribers': str([subscriber.channel_name for subscriber in user.followers])
        }
        return jsonify({'user': result})


class UserListApi(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('username', required=True)
    parser.add_argument('channel_name', required=True)
    parser.add_argument('email', required=True)
    parser.add_argument('birthday', required=True)
    parser.add_argument('interests', required=True)
    parser.add_argument('about_channel', required=True)
    parser.add_argument('meta_tags', required=True)
    parser.add_argument('password', required=True)

    def post(self):
        args = self.parser.parse_args()
        try:
            birthday = args['birthday']
            datetime.datetime.strptime(birthday, '%d.%m.%Y')
        except ValueError:
            return jsonify({'error': 'Incorrect birthday format dd.mm.YYYY'})
        if User.query.filter_by(username=args['username']).first() is not None:
            return jsonify({'error': 'Such user is already register'})
        user = User(username=args['username'], channel_name=args['channel_name'], email=args['email'], birthday=datetime.datetime.strptime(birthday, '%d.%m.%Y'), about_channel=args['about_channel'])
        user.set_password(args['password'])
        interest = args['interests'].split('.')
        for i in range(len(interest)):
            interest[i] = interest[i].lower().rstrip().lstrip()
            if len(interest[i]) >= 256:
                continue
            if Interests.query.filter_by(text=interest[i]).first() is None:
                db.session.add(Interests(text=interest[i]))
            if Interests.query.filter_by(text=interest[i]).first() not in user.interests:
                user.interests.append(Interests.query.filter_by(text=interest[i]).first())
            db.session.commit()

        meta_tags = args['meta_tags'].split('.')
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
        return jsonify({'success': 'OK'})


api.add_resource(UserApi, '/api/users/<int:user_id>')
api.add_resource(UserListApi, '/api/users')
