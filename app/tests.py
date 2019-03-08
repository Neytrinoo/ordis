import unittest
from app import app, db
from app.models import User, MetaTags, Interests
from datetime import datetime, timedelta
from zipfile import ZipFile

class UserModelCase(unittest.TestCase):
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_user_registration(self):
        u1 = User(username='user1', channel_name='user1_channel',
                  email='user1@mail.ru', birthday=datetime.utcnow(),
                  about_channel='user1 about channel')
        int1 = Interests(text='программирование')
        int2 = Interests(text='python')
        db.session.add_all([int1, int2, u1])
        db.session.commit()
        self.assertEqual(len(u1.interests), 0)
        u1.interests.append(int1)
        u1.interests.append(int2)
        self.assertEqual(len(u1.interests), 2)
        self.assertEqual(len(u1.meta_tags), 0)
        tag1 = MetaTags(text='python')
        tag2 = MetaTags(text='чтение')
        tag3 = MetaTags(text='книги')
        db.session.add_all([tag1, tag2, tag3])
        db.session.commit()
        u1.meta_tags.append(tag1)
        u1.meta_tags.append(tag2)
        u1.meta_tags.append(tag3)
        self.assertEqual(len(u1.meta_tags), 3)
        self.assertEqual(tag1.users.count(), 1)


if __name__ == '__main__':
    unittest.main(verbosity=2)
