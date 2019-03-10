from flask_restful import reqparse, abort, Api, Resource
from app import app, db
from app.models import User, SingleLesson, MetaTags, Interests, LessonComment, MetaTagsLesson
from flask import jsonify
import datetime
from os.path import join, dirname, realpath

api = Api(app)


def abort_if_lesson_not_found(id):
    if SingleLesson.query.filter_by(id=id).first() is None:
        abort(404, message="Lesson {} not found".format(id))


def abort_if_user_not_found(id):
    if User.query.filter_by(id=id).first() is None:
        abort(404, message="User {} not found".format(id))


def abort_if_comment_not_found(id):
    if LessonComment.query.filter_by(id=id).first() is None:
        abort(404, message="Comment {} not found".format(id))


def abort_if_username_or_password_do_not_match(user_id, username, password):
    user = User.query.filter_by(id=user_id).one()
    if not user.check_password(password) or user.username != username:
        abort(404, message='username or password do not match')


def abort_if_username_or_password_does_not_match(username, password):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404, message='Username {} is not register'.format(username))
    if not user.check_password(password):
        abort(404, message='username or password do not match')


class UserApi(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('password', required=True)
    parser.add_argument('username', required=True)
    parser.add_argument('channel_name', required=False)
    parser.add_argument('interests', required=False)
    parser.add_argument('about_channel', required=False)
    parser.add_argument('meta_tags', required=False)
    parser.add_argument('new_password', required=False)
    parser.add_argument('new_username', required=False)

    def get(self, user_id):
        abort_if_user_not_found(user_id)
        user = User.query.filter_by(id=user_id).first()
        result = {
            'birthday': user.birthday,
            'username': user.username,
            'channel_name': user.channel_name,
            'meta-tags': ','.join([text.text for text in user.meta_tags]),
            'subscribers': ','.join([subscriber.channel_name for subscriber in user.followers])
        }
        return jsonify({'user': result})

    def delete(self, user_id):
        abort_if_user_not_found(user_id)
        args = self.parser.parse_args()
        try:
            user = User.query.filter_by(id=user_id).one()
            abort_if_username_or_password_do_not_match(user_id, args['username'], args['password'])
            db.session.delete(user)
            db.session.commit()
            return jsonify({'success': 'OK'})
        except Exception as e:
            return jsonify({'error': 'an error occurred'})

    def put(self, user_id):
        abort_if_user_not_found(user_id)
        args = self.parser.parse_args()
        try:
            user = User.query.filter_by(id=user_id).one()
            abort_if_username_or_password_do_not_match(user_id, args['username'], args['password'])
            if args['new_username'] is not None:
                if User.query.filter_by(username=args['new_username']).first() is not None:
                    return jsonify({'error': 'Such username is already register'})
                user.username = args['new_username']

            if args['channel_name'] is not None:
                user.channel_name = args['channel_name']

            if args['interests'] is not None:
                interest = args['interests'].split(',')
                for i in range(len(interest)):
                    interest[i] = interest[i].lower().rstrip().lstrip()
                    if len(interest[i]) >= 256:
                        continue
                    if Interests.query.filter_by(text=interest[i]).first() is None:
                        db.session.add(Interests(text=interest[i]))
                    if Interests.query.filter_by(text=interest[i]).first() not in user.interests:
                        user.interests.append(Interests.query.filter_by(text=interest[i]).first())
                    db.session.commit()

            if args['meta_tags'] is not None:
                meta_tags = args['meta_tags'].split(',')
                for i in range(len(meta_tags)):
                    meta_tags[i] = meta_tags[i].lower().rstrip().lstrip()
                    if len(meta_tags[i]) >= 256:
                        continue
                    if MetaTags.query.filter_by(text=meta_tags[i]).first() is None:
                        db.session.add(MetaTags(text=meta_tags[i]))
                    if MetaTags.query.filter_by(text=meta_tags[i]).first() not in user.meta_tags:
                        user.meta_tags.append(MetaTags.query.filter_by(text=meta_tags[i]).first())
                    db.session.commit()

            if args['about_channel'] is not None:
                user.about_channel = args['about_channel']

            if args['new_password'] is not None:
                user.set_password(args['new_password'])

            db.session.commit()
            return jsonify({'success': 'OK'})
        except Exception as e:
            return jsonify({'error': 'An error occurred'})


class UserListApi(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('username', required=True)
    parser.add_argument('channel_name', required=False)
    parser.add_argument('email', required=False)
    parser.add_argument('birthday', required=False)
    parser.add_argument('interests', required=False)
    parser.add_argument('about_channel', required=False)
    parser.add_argument('meta_tags', required=False)
    parser.add_argument('password', required=True)

    def get(self):
        users = User.query.all()
        all_users = {}
        for user in users:
            result = {
                'id': user.id,
                'birthday': user.birthday,
                'username': user.username,
                'channel_name': user.channel_name,
                'meta-tags': ','.join([text.text for text in user.meta_tags]),
                'subscribers': ','.join([subscriber.username for subscriber in user.followers])
            }
            all_users[user.id] = result
        return jsonify({'users': all_users})

    def post(self):
        args = self.parser.parse_args()
        try:
            birthday = args['birthday']
            datetime.datetime.strptime(birthday, '%d.%m.%Y')
        except ValueError:
            return jsonify({'error': 'Incorrect birthday format dd.mm.YYYY'})
        if User.query.filter_by(username=args['username']).first() is not None:
            return jsonify({'error': 'Such user is already register'})
        if User.query.filter_by(email=args['email']).first() is not None:
            return jsonify({'error': 'User with this email is already registered'})
        file = open(join(dirname(realpath(__file__)), 'static/img/user_default_avatar.png'), 'rb').read()
        user = User(username=args['username'], channel_name=args['channel_name'], email=args['email'], birthday=datetime.datetime.strptime(birthday, '%d.%m.%Y'),
                    about_channel=args['about_channel'], avatar=file)
        user.set_password(args['password'])

        interest = args['interests'].split(',')
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


class SingleLessonApi(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('username')
    parser.add_argument('password')
    parser.add_argument('lesson_name')
    parser.add_argument('about_lesson')
    parser.add_argument('extra_material')
    parser.add_argument('meta_tags')

    def get(self, id):
        abort_if_lesson_not_found(id)
        lesson = SingleLesson.query.filter_by(id=id).first()
        result = {
            'lesson_name': lesson.lesson_name,
            'about_lesson': lesson.about_lesson,
            'extra_material': lesson.extra_material,
            'views': lesson.views,
            'meta_tags': ','.join([text.text for text in lesson.meta_tags]),
            'author': lesson.user.username,
            'author_id': lesson.user_id,
            'rating': lesson.rating,
            'date_added': lesson.date_added,
            'comments': {}
        }
        for comment in lesson.comments:
            result['comments'][comment.id] = {'comment_id': comment.id, 'user_id': comment.user_id}
        return jsonify({'lesson': result})

    def delete(self, id):
        try:
            args = self.parser.parse_args()
            lesson = SingleLesson.query.filter_by(id=id).first()
            user = lesson.user
            abort_if_username_or_password_do_not_match(user.id, args['username'], args['password'])
            db.session.delete(lesson)
            db.session.commit()
            return jsonify({'success': 'OK'})
        except Exception as e:
            return jsonify({'error': 'An error occurred'})

    def put(self, id):
        abort_if_lesson_not_found(id)
        args = self.parser.parse_args()
        try:
            lesson = SingleLesson.query.filter_by(id=id).one()
            abort_if_username_or_password_do_not_match(lesson.user_id, args['username'], args['password'])

            if args['lesson_name'] is not None:
                lesson.lesson_name = args['lesson_name']

            if args['about_lesson'] is not None:
                lesson.about_lesson = args['about_lesson']

            if args['extra_material'] is not None:
                lesson.extra_material = args['extra_material']

            if args['meta_tags'] is not None:
                meta_tags = args['meta_tags'].split(',')
                for i in range(len(meta_tags)):
                    meta_tags[i] = meta_tags[i].lower().rstrip().lstrip()
                    if len(meta_tags[i]) >= 600:
                        continue
                    if MetaTagsLesson.query.filter_by(text=meta_tags[i]).first() is None:
                        db.session.add(MetaTagsLesson(text=meta_tags[i]))
                    if MetaTagsLesson.query.filter_by(text=meta_tags[i]).first() not in lesson.meta_tags:
                        lesson.meta_tags.append(MetaTagsLesson.query.filter_by(text=meta_tags[i]).first())
                    db.session.commit()

            db.session.commit()
            return jsonify({'success': 'OK'})
        except Exception as e:
            return jsonify({'error': 'An error occurred'})


class SingleLessonListApi(Resource):
    def get(self):
        lessons = SingleLesson.query.all()
        all_lessons_json = {}
        for lesson in lessons:
            result = {
                'lesson_name': lesson.lesson_name,
                'lesson_id': lesson.id,
                'about_lesson': lesson.about_lesson,
                'extra_material': lesson.extra_material,
                'views': lesson.views,
                'meta_tags': ','.join([text.text for text in lesson.meta_tags]),
                'author': lesson.user.username,
                'author_id': lesson.user_id,
                'rating': lesson.rating,
                'date_added': lesson.date_added,
                'comments': {}
            }
            for comment in lesson.comments:
                result['comments'][comment.id] = {'comment_id': comment.id, 'user_id': comment.user_id}
            all_lessons_json[lesson.id] = result
        return jsonify({'lessons': all_lessons_json})


class CommentApi(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('username', required=True)
    parser.add_argument('password', required=True)
    parser.add_argument('text', required=False)
    parser.add_argument('rating', required=False)

    def get(self, id):
        abort_if_comment_not_found(id)
        comment = LessonComment.query.filter_by(id=id).first()
        result = {
            'text': comment.text,
            'rating': comment.rating,
            'lesson_id': comment.lesson_id,
            'user_id': comment.user_id
        }
        return jsonify({'comment': result})

    def delete(self, id):
        args = self.parser.parse_args()
        abort_if_username_or_password_does_not_match(args['username'], args['password'])
        abort_if_comment_not_found(id)
        user = User.query.filter_by(username=args['username']).first()
        comment = LessonComment.query.filter_by(id=id).first()
        lesson = SingleLesson.query.filter_by(id=comment.lesson_id).first()
        if comment.user_id != user.id:
            return jsonify({'error': 'The user {} did not leave this comment'.format(args['username'])})
        lesson_comments = -1
        for com in user.comments:
            if com.lesson_id == comment.lesson_id:
                lesson_comments = com
                break
        # Изменяем рейтинг урока только в том случае, если это был первый комментарий пользователя
        if lesson_comments.id == comment.id:
            lesson.rating_sum -= comment.rating
            lesson.rating = lesson.rating_sum / (len(lesson.comments) - 1)
        db.session.delete(comment)
        db.session.commit()
        return jsonify({'success': 'OK'})

    def put(self, id):
        args = self.parser.parse_args()
        abort_if_username_or_password_does_not_match(args['username'], args['password'])
        abort_if_comment_not_found(id)
        user = User.query.filter_by(username=args['username']).first()
        comment = LessonComment.query.filter_by(id=id).first()
        lesson = SingleLesson.query.filter_by(id=comment.lesson_id).first()
        if comment.user_id != user.id:
            return jsonify({'error': 'The user {} did not leave this comment'.format(args['username'])})
        if args['text'] is not None:
            comment.text = args['text']
        if args['rating'] is not None:
            lesson_comments = -1
            for com in user.comments:
                if com.lesson_id == comment.lesson_id:
                    lesson_comments = com
                    break
            if lesson_comments.id == comment.id:
                lesson.rating_sum -= comment.rating
                lesson.rating_sum += float(args['rating'])
                lesson.rating = lesson.rating_sum / (len(lesson.comments))
            comment.rating = float(args['rating'])
        db.session.commit()
        return jsonify({'success': 'OK'})


class CommentListApi(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('username', required=True)
    parser.add_argument('password', required=True)
    parser.add_argument('text', required=True)
    parser.add_argument('lesson_id', required=True)
    parser.add_argument('rating', required=True)

    def post(self):
        args = self.parser.parse_args()
        try:
            abort_if_username_or_password_does_not_match(args['username'], args['password'])
            abort_if_lesson_not_found(args['lesson_id'])
            lesson = SingleLesson.query.filter_by(id=args['lesson_id']).first()
            user = User.query.filter_by(username=args['username']).first()
            if float(args['rating']) < 0 or float(args['rating']) > 10:
                return jsonify({'error': 'The rating can range from 0 to 10'})
            if float(args['rating']) != int(float(args['rating'])):
                return jsonify({'error': 'The rating can be integer, not float'})
            comment = LessonComment(text=args['text'], rating=float(args['rating']))
            change_rating = True
            for comment in user.comments:
                if comment.lesson_id == lesson.id:
                    change_rating = False

            # Общий рейтинг урока изменяется только в том случае, если данный пользователь оставил свой первый комментарий
            if change_rating:
                lesson.rating_sum += float(args['rating'])
                lesson.rating = lesson.rating_sum / (len(lesson.comments) + 1)

            lesson.comments.append(comment)
            user.comments.append(comment)
            db.session.commit()
            return jsonify({'success': 'OK'})
        except Exception as e:
            return jsonify({'error': 'An error occurred'})


api.add_resource(UserApi, '/api/users/<int:user_id>')
api.add_resource(UserListApi, '/api/users')
api.add_resource(SingleLessonApi, '/api/lessons/<int:id>')
api.add_resource(SingleLessonListApi, '/api/lessons')
api.add_resource(CommentApi, '/api/comments/<int:id>')
api.add_resource(CommentListApi, '/api/comments')
