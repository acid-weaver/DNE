from utils.tests import BaseTestCaseAPI
from rest_framework.reverse import reverse


class TestUser(BaseTestCaseAPI):

    def test_user_registration(self):
        body = {
            'username': 'Ama test user from tests!!!!',
            'password': 'somestupidpassword',
            'first_name': 'Jacob',
            'last_name': 'Niclson'
        }
        url = reverse("user-list")
        response = self.anon_client.post(url, body)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['username'], body['username'])
        self.assertEqual(response.data['first_name'], body['first_name'])
        self.assertEqual(response.data['last_name'], body['last_name'])

        # same username as before
        response = self.anon_client.post(url, body)
        self.assertEqual(response.status_code, 400)

        # short password
        body['username'] = 'Ama anoser test user from tests'
        body['password'] = '123'
        response = self.anon_client.post(url, body)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['username'], body['username'])
        self.assertEqual(response.data['first_name'], body['first_name'])
        self.assertEqual(response.data['last_name'], body['last_name'])
        # print(response.status_code)
        # print(response.data)
