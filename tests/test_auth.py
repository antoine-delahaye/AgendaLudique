import json
import unittest
from base64 import b64encode

from flask_login import current_user

from app import db, create_app
from app.models import User


class AUTHTest(unittest.TestCase):

    # executed prior to each test
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()

        self.client = self.app.test_client()

    # executed after each test
    def tearDown(self):
        db.session.remove()
        db.session.rollback()
        self.app_context.pop()

    def register(self, email, password, confirm):
        with self.app.test_client():
            return self.client.post(
                '/auth/register',
                data=json.dumps({'email': email, 'password': password}),
                follow_redirects=True
            )

    def login(self, email, password):
        with self.app.test_client():
            return self.client.post(
                '/auth/register',
                data=json.dumps({'email': email, 'password': password}),
                follow_redirects=True
            )

    def logout(self):
        return self.client.get(
            '/auth/logout',
            follow_redirects=True
        )

    def get_api_headers(self, username, password):
        return {
            'Authorization': 'Basic ' + b64encode(
                (username + ':' + password).encode('utf-8')).decode('utf-8'),
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            "follow_redirects": True
        }

    def working_page(self):
        for route in self.app.url_map.iter_rules():
            response = self.client.get(route)
            self.assertLess(response.status_code, 400)

    def test_404(self):
        response = self.client.get(
            '/wrong/url',
            headers=self.get_api_headers('email', 'password'))
        self.assertEqual(response.status_code, 404)

    def test_no_auth(self):
        response = self.client.get('/catalog',
                                   content_type='application/json')
        self.assertEqual(response.status_code, 302)
        response = self.client.get('/group',
                                   content_type='application/json')
        self.assertEqual(response.status_code, 302)

    def test_bad_auth(self):
        # add a user
        u = User(email='BobLeMusclé', password_hash='cat', username="Bobby")
        db.session.add(u)
        db.session.flush()

        response = self.login("BobLeMusclé@dev.good", "dog")

        self.assertEqual(response.status_code, None)

    def test_good_auth(self):
        # add a user
        u = User(email='BobLeMusclé@dev.good', password_hash='cat', username="Bobby")
        db.session.add(u)
        db.session.flush()

        response = self.login("BobLeMusclé@dev.good", "cat")
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()
