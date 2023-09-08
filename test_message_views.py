"""Message View tests."""

# run these tests like:
#
#    FLASK_DEBUG=False python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, Message, User, Like

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

# Now we can import app

from app import app, CURR_USER_KEY

app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

# This is a bit of hack, but don't use Flask DebugToolbar

app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.drop_all()
db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageBaseViewTestCase(TestCase):
    def setUp(self):
        """Instantiates user and message before every test"""
        Like.query.delete()
        Message.query.delete()
        User.query.delete()

        u2 = User.signup("u2", "u2@email.com", "password", None)
        u1 = User.signup("u1", "u1@email.com", "password", None)
        db.session.add_all([u1, u2])
        db.session.flush()

        m1 = Message(text="m1-text", user_id=u1.id)
        m2 = Message(text="m2-text", user_id=u1.id)

        db.session.add_all([m1, m2])
        db.session.commit()

        l1 = Like(user_id=u2.id, message_id=m1.id)
        db.session.add(l1)
        db.session.commit()

        self.u2_id = u2.id
        self.u1_id = u1.id
        self.m1_id = m1.id
        self.m2_id = m2.id

        self.client = app.test_client()


    def tearDown(self):
        """Cleans up any database transactions"""
        db.session.rollback()


class MessageAddViewTestCase(MessageBaseViewTestCase):
    def test_add_message(self):
        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            # Now, that session setting is saved, so we can have
            # the rest of ours test
            resp = c.post("/messages/new", data={"text": "Hello"})

            self.assertEqual(resp.status_code, 302)

            self.assertTrue(Message.query.filter_by(text="Hello").one())

    def test_add_message_auth(self):
        """Test authorization on add message route"""
        with self.client as c:

            resp = c.post("/messages/new", data={"text": "Hello"}, follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)

            self.assertIn("Access unauthorized", html)

    def test_delete_message(self):
        """Test functionality of message delete"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id
            
            resp = c.post(f"/messages/{self.m1_id}/delete")

            self.assertEqual(resp.status_code, 302)

            self.assertFalse(Message.query.filter_by(id=self.m1_id).one_or_none())

    def test_delete_redirect(self):
        """Test redirect of message delete"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id
            
            resp = c.post(f"/messages/{self.m1_id}/delete", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)

            self.assertIn("TEST REDIRECT DELETE", html)


    def test_delete_message_auth(self):
        """Ensures only message owner can delete message"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u2_id

            resp = c.post(f"/messages/{self.m1_id}/delete", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)

            self.assertIn("Access unauthorized", html)


    def test_show_message(self):
        """Test message show page"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id
            
            resp = c.get(f"/messages/{self.m1_id}")

            self.assertEqual(resp.status_code, 200)

            html = resp.get_data(as_text=True)

            self.assertIn("TEST SHOW MESSAGE", html)

        
    def test_like_message(self):
        """Test liking a message functionality"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u2_id
            
            resp = c.post(f"/users/like/{self.m2_id}")

            self.assertEqual(resp.status_code, 302)

            self.assertEqual(resp.location, f"/users/{self.u2_id}/likes")


    def test_like_redirect(self):
        """Test redirect after liking a message"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u2_id
            
            resp = c.post(f"/users/like/{self.m2_id}", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)

            self.assertIn("TEST REDIRECT LIKE MESSAGE", html)


    def test_unlike_message(self):
        """Test unlike functionality of message"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u2_id
            
            resp = c.post(f"/users/unlike/{self.m1_id}")

            self.assertEqual(resp.status_code, 302)

            self.assertEqual(resp.location, f"/users/{self.u2_id}/likes")


    def test_unlike_redirect(self):
        """Test redirect of unliking a message"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u2_id
            
            unlike_resp = c.post(f"/users/unlike/{self.m1_id}", follow_redirects=True)
            html = unlike_resp.get_data(as_text=True)

            self.assertEqual(unlike_resp.status_code, 200)

            self.assertIn("TEST REDIRECT UNLIKE MESSAGE", html)
