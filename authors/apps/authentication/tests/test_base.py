from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from ..models import User
import json
from ..backends import AccountVerification


class TestBase(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.url = reverse("authentication:login")
        self.register_url = reverse("authentication:register")
        self.acc_verify = AccountVerification
        self.known_key = 'InRlc3QyQHRlc3R1c2VyLmNvbSI.XPwXBQ.-MB4H7ykcxDwYSUw3HzvIeCo82k'
        self.invalid_key = 'InRoeS5yZWFsZXJzQGdtYWlsLmNvbSI.XPkRcg.37n9xSNEqhyM9V_z94z-Q9vLQWwInvalid'
        self.user_data = {
            'user': {
                'email': "test@testuser.com",
                'username': "testuser",
                'password': "password"
            }
        }
        self.user_data_2 = {
            'user': {
                'email': "test2@testuser.com",
                'username': "testuser2",
                'password': "password2"
            }
        }
        self.new_test_user = self.client.post(
            self.register_url, self.user_data, format="json")

        self.new_test_user_2 = self.client.post(
            self.register_url, self.user_data_2, format="json")

        # verifies user 1 account upon signup
        self.acc_verify.verify_user(self.user_data['user']['email'])

        # use the APIClient to log in the user to be tested against
        self.logged_in_user = self.client.post(
            self.url, self.user_data, format="json")

        # individualise these to easily test against them
        self.username = "neelxie"
        self.email = "derek@derek.com"
        self.password = "realers"

        # create user for models tests
        self.new_db_user = User(
            email=self.email,
            password=self.password,
            username=self.username)

        # Getting the token
        self.token = self.logged_in_user.data.get("token")
