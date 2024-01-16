"""Message model tests."""

# run these tests like:
#
#   python -m unittest test_message_model.py
#   ↓ Use this so it doesn't run Debug Toolbar ↓
#   FLASK_ENV=production python -m unittest test_message_model.py


import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Message, Follows, Likes

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

        db.session.commit()

        user1 = User.query.get(user_id1)

        self.user1 = user1
        self.user_id1 = user_id1

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_message_model(self):
        """Does basic model work?"""

        m = Message(
            text="test message text",
            user_id=self.user_id1
        )

        db.session.add(m)
        db.session.commit()

        # User should have 1 messages with text 'test message text'
        self.assertEqual(len(self.user1.messages), 1)
        self.assertEqual(self.user1.messages[0].text, 'test message text')


    def test_messages_likes(self):
        """"""
        
        m1 = Message(
            text="message 1 test text",
            user_id=self.user_id1
        )
        m2 = Message(
            text="message 2 test text",
            user_id=self.user_id1
        )

        db.session.add_all([m1, m2])
        db.session.commit()

        self.user1.likes.append(m1)
        db.session.commit()

        l = Likes.query.filter(Likes.user_id == self.user_id1).all()
        self.assertEqual(len(l), 1)
        self.assertEqual(l[0].message_id, m1.id)

   #  def test_messages_show(self):
   #      """"""

   #      show_message = Message(
   #          text="show message test text",
   #          user_id=self.user_id1
   #      )
   #      db.session.add(show_message)
   #      db.session.commit()

   
   #  def test_messages_delete(self):
   #      """"""
