from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from ..models import User
from ..backends import AccountVerification


class TestBase(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.url = reverse("authentication:login")
        self.register_url = reverse("authentication:register")
        self.acc_verify = AccountVerification
        self.known_key = "InRlc3QyQHRlc3R1c2VyLmNvbSI.XPwXBQ.-MB4H7ykcxDwYSUw3HzvIeCo82k"
        self.invalid_key = "InRoeS5yZWFsZXJzQGdtYWlsLmNvbSI.XPkRcg.37n9xSNEqhyM9V_z94z-Q9vLQWwInvalid"
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

        # create user when email is invalid
        self.user_data1 = {
            'user': {
                'email': "jenny.com",
                'username': "jennyj23",
                'password': "jenny1234"
            }
        }
        self.new_user = self.client.post(
            self.register_url, self.user_data1, format="json")

        # create user when username is existing
        self.user_data11 = {
            'user': {
                'email': "jenny@gmail.com",
                'username': "jenny23",
                'password': "jenny1234"
            }
        }
        self.user_with_username_exist = self.client.post(
            self.register_url, self.user_data11, format="json")


        # create email twice
        self.user_data12 = {
            'user': {
                'email': "jenny@gmail.com",
                'username': "jen23",
                'password': "jenny1234"
            }
        }
        self.user_email_exit = self.client.post(
            self.register_url, self.user_data12, format="json")

        # create user when password is invalid
        self.user_data1 = {
            'user': {
                'email': "jenny23@gmail.com",
                'username': "jenny23",
                'password': "j1234"
            }
        }
        self.new_user2 = self.client.post(
            self.register_url, self.user_data1, format="json")

        # create user when password is empty
        self.recevied_data1 = {
            'user': {
                'email': "jenny23@gmail.com",
                'username': "jennyhyy",
                'password': ""
            }
        }
        self.new_users2 = self.client.post(
            self.register_url, self.recevied_data1, format="json")

        # create user when username has special characters
        self.recevied_data = {
            'user': {
                'email': "jenny23@gmail.com",
                'username': "jen_nny_123",
                'password': "jenny1234"
            }
        }
        self.new_users = self.client.post(
            self.register_url, self.recevied_data, format="json")
