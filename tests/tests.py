import unittest
import sys
sys.path.insert(0,'..')  # Upload parent directory
from app import app
from flask import session


class Flask_test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print('setUpClass\n')

    @classmethod
    def tearDownClass(cls):
        print('tearDownClass')


    def setUp(self):
        print('setUp')
        app.config['TESTING'] = False


    def tearDown(self):
        print('tearDown\n')
        pass


    # Check for header "<h4>" in html code
    def test_root(self):
        print('test_root')
        tester = app.test_client(self)
        response = tester.get('/')
        assert b"<h4>Worker login</h4>" in response.data


    # Check logout redirects
    def test_logout(self):
        print('test_logout')
        tester = app.test_client(self)
        response = tester.get('/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)


    # Check login has a session['username']
    def test_login(self):
        print('test_login')
        with (app.test_client()) as client:
            client.post("/check_username", data={
                "username": "John",
                "password": "john123",
            })
            assert session["username"] == 'John'


if __name__ == '__main__':
    unittest.main()

