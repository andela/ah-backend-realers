from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from authors.apps.authentication.tests.test_base import TestBase as UserTestBaseCase


class ProfileTestBase(UserTestBaseCase):

    def setUp(self):
        super().setUp()

        self.valid_user_profile = {
            "profile": {
                "bio":"I am professional code tester",
                "gender": "male",
                "first_name": "Thy",
                "last_name": "Realers",
                "location": "Kampala",
                "birth_date": "2019-05-06"
            }
        }

        self.profile_invalid_firstname = {
            "profile": {
                "first_name": "89ehwjkewr",
                "last_name": "Realers",
            }
        }

        self.profile_invalid_lastname = {
            "profile": {
                "first_name": "Thy",
                "last_name": "23908592359",
            }
        }