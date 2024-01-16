"""User model tests."""

# run these tests like:
#
#   python -m unittest test_user_model.py
#   ↓ Use this so it doesn't run Debug Toolbar ↓
#   FLASK_ENV=production python -m unittest test_user_model.py


import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        # User.query.delete()
        # Message.query.delete()
        # Follows.query.delete()

        db.drop_all()
        db.create_all()

        user1 = User.signup("test_user_1", "test_user_1@email.com", "pass1", "")
        user_id1 = 1111
        user1.id = user_id1

        user2 = User.signup("test_user_2", "test_user_2@email.com", "pass2", "")
        user_id2 = 2222
        user2.id = user_id2

        db.session.commit()

        user1 = User.query.get(user_id1)
        user2 = User.query.get(user_id2)

        self.user1 = user1
        self.user_id1 = user_id1

        self.user2 = user2
        self.user_id2 = user_id2

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)


    def test_user_follows(self):
        self.user1.following.append(self.user2)
        db.session.commit()

        self.assertEqual(len(self.user1.following), 1)
        self.assertEqual(len(self.user1.followers), 0)
        self.assertEqual(len(self.user2.following), 0)
        self.assertEqual(len(self.user2.followers), 1)

        self.assertEqual(self.user1.following[0].id, self.user2.id)
        self.assertEqual(self.user2.followers[0].id, self.user1.id)

    def test_is_following(self):
        self.user1.following.append(self.user2)
        db.session.commit()

        self.assertTrue(self.user1.is_following(self.user2))
        self.assertFalse(self.user2.is_following(self.user1))


    def test_is_followed_by(self):
        self.user1.following.append(self.user2)
        db.session.commit()

        self.assertTrue(self.user2.is_followed_by(self.user1))
        self.assertFalse(self.user1.is_followed_by(self.user2))

    
    ### Sign Up Tests

    def test_valid_signup(self):
        u_test = User.signup("test_signup_user", "test_signup@email.com", "pass1", "")
        uid = 999
        u_test.id = uid
        db.session.commit()

        u_test = User.query.get(uid)
        self.assertIsNotNone(u_test)
        self.assertEqual(u_test.username, "test_signup_user")
        self.assertEqual(u_test.email, "test_signup@email.com")
        self.assertNotEqual(u_test.password, "pass1")
        # Bcrypt strings should start with $2b$
        self.assertTrue(u_test.password.startswith("$2b$"))

    def test_invalid_username_signup(self):
        invalid = User.signup(None, "test_signup@email.com", "pass1", "")
        uid = 12345
        invalid.id = uid
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_invalid_email_signup(self):
        invalid = User.signup("test_signup_user", None, "pass1", "")
        uid = 12345
        invalid.id = uid
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_invalid_password_signup(self):
        with self.assertRaises(ValueError) as context:
            User.signup("test_signup_user", "test_signup@email.com", "", None)
        
        with self.assertRaises(ValueError) as context:
            User.signup("test_signup_user", "test_signup@email.com", None, None)


### Authentication Tests
            

    def test_valid_authentication(self):
        auth_user = User.authenticate(self.user1.username, "pass1")
        self.assertIsNotNone(auth_user)
        self.assertEqual(auth_user.id, self.user_id1)
    
    def test_invalid_username(self):
        self.assertFalse(User.authenticate("badusername", "password"))

    def test_wrong_password(self):
        self.assertFalse(User.authenticate(self.user1.username, "badpassword"))