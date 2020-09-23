from datetime import datetime, timedelta
import unittest
from server import app, engine, createTables, destroyTables, SQLSession
from hgossipBack.models.meta import Base
from hgossipBack.models import Post, User
from hgossipBack.config import DbEngine_config

from flask_sqlalchemy import SQLAlchemy
Base = SQLAlchemy(app)


# TODO There is no metadata is attached to the base so the tables are not found by the unit test


class UserModelCase(unittest.TestCase):
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        Base.metadata.bind = engine
        Base.metadata.create_all()
        print('Initialize the database!')


    def tearDown(self):
        Base.session.remove()
        Base.metadata.drop_all()
        print('Droped the database!')


    def test_password_hashing(self):
        u = User(username='harry')
        u.set_password('12345')
        self.assertFalse(u.check_password('123'))
        self.assertTrue(u.check_password('12345'))


    def test_avatar(self):
        u = User(username='john', email='john@example.com')
        self.assertEqual(u.avatar(128), ('https://www.gravatar.com/avatar/'
                                         'd4c74594d841139328695756648b6bd6'
                                         '?d=identicon&s=128'))


    def test_follow(self):
        u1 = User(username='harry', email='harry123@gmail.com')
        u2 = User(username='annu', email='annu123@gmail.com')
        Base.session.add(u1)
        Base.session.add(u2)
        Base.session.commit()
        self.assertEqual(u1.followed.all(), [])
        self.assertEqual(u1.followers.all(), [])

        u1.follow(u2)
        Base.session.commit()
        self.assertTrue(u1.is_following(u2))
        self.assertEqual(u1.followed.count(), 1)
        self.assertEqual(u1.followed.first().username, 'annu')
        self.assertEqual(u2.followers.count(), 1)
        self.assertEqual(u2.followers.first().username, 'harry')

        u1.unfollow(u2)
        Base.session.commit()
        self.assertFalse(u1.is_following(u2))
        self.assertEqual(u1.followed.count(), 0)
        self.assertEqual(u2.followers.count(), 0)


    def test_follow_posts(self):
        u1 = User(username='harry', email='harry123@gmail.com')
        u2 = User(username='annu', email='annu123@gmail.com')
        u3 = User(username='kajal', email='kajal123@gmail.com')
        u4 = User(username='urmila', email='urmila123@gmail.com')
        Base.session.add_all([u1, u2, u3,u4])
        u1_id = u1.id
        u2_id = u2.id
        u3_id = u3.id
        u4_id = u4.id

        now = datetime.utcnow()
        p1 = Post(body="post from harry", user_id=u1_id, timestamp=now+timedelta(seconds=1))
        p2 = Post(body="post from annu", user_id=u2_id, timestamp=now+timedelta(seconds=4))
        p3 = Post(body="post from kajal", user_id=u3_id, timestamp=now+timedelta(seconds=3))
        p4 = Post(body="post from urmila", user_id=u4_id, timestamp=now+timedelta(seconds=2))
        Base.session.add_all([p1, p2, p3, p4])
        Base.session.commit()

        u1.follow(u2)
        u1.follow(u4)
        u2.follow(u3)
        u3.follow(u4)
        Base.session.commit()

        f1 = u1.followed_posts().all()
        f2 = u2.followed_posts().all()
        f3 = u3.followed_posts().all()
        f4 = u4.followed_posts().all()
        self.assertEqual(f1, [p1, p4, p1])
        self.assertEqual(f2, [p2, p3])
        self.assertEqual(f3, [p3, p4])
        self.assertEqual(f4, [p4])


if __name__ == '__main__':
    unittest.main(verbosity=2)
