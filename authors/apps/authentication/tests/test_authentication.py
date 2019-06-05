from .test_base import TestBase
import json
from rest_framework import status
from ..models import User


class UserRegistrationAPIViewTestCase(TestBase):

    def test_user_registration(self):
        """
        Test to verify that a post call with user valid data
        """
        output = "Please check your email and verify your registration"
        result = json.loads(self.new_test_user.content)
        self.assertEquals(201, self.new_test_user.status_code)
        self.assertEqual("testuser", result['user']['username'])
        self.assertIn(output, str(result))

    def test_user_with_invalid_email(self):
        self.user_data = {
            "user": {
                "email": "",
                "username": "jenny",
                "password": "123jemnny",
                "bio": "l am a writer",
                "image": "linking"
            }
        }
        self.new_test_user = self.client.post(
            self.register_url, self.user_data, format="json")
        self.assertEqual(400, self.new_test_user.status_code)
        self.assertRaises(TypeError)

    def test_user_with_invalid_password(self):
        self.user_data = {
            "user": {
                "email": "jenny@gmail",
                "username": "jenny",
                "password": "123",
                "bio": "l am a writer",
                "image": "the link"
            }
        }
        self.the_new_user = self.client.post(
            self.register_url, self.user_data, format="json")
        self.assertEqual(400, self.the_new_user.status_code)
        self.assertRaises(TypeError)

class UserLoginAPIViewTestCase(TestBase):
    """ 
    Test to test the loginAPIView in the views file.
    """

    def test_login_for_signed_up_user(self):

        self.assertEquals("test@testuser.com",
                          self.logged_in_user.data["email"])
        self.assertEqual(self.logged_in_user.status_code, status.HTTP_200_OK)
        self.assertIn('token', self.logged_in_user.data)

    def test_login_with_no_email(self):

        response = self.client.post(
            self.url,
            {"user": {
                "password": "donthack"
            }},
            format="json")

        self.assertIn(
            'This field is required.',
            response.data["errors"]["email"]
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_with_wrong_email_and_wrong_password(self):

        response = self.client.post(
            self.url,
            {"user": {
                "email": "emma@realers.com",
                "password": "donthack"
            }},
            format="json")

        self.assertIn(
            'A user with this email and password was not found.',
            response.data["errors"]["error"]
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserRetrieveUpdateAPIViewTestCase(TestBase):
    """
    A test class that tests the RetrieveUpdateAPIView class in the views
    file 
    """

    def test_fetch_user_from_system_with_valid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(self.token))
        response = self.client.get(
            # unlike other routes this has no key name
            # touse to refer to it in the urls file
            '/api/user/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_fetch_user_from_system_with_Invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer jhgsjfudstuydsfj')
        response = self.client.get('/api/user/')
        self.assertIn("Invalid token", str(response.data))

    def test_fetch_user_from_system_with_no_token(self):
        response = self.client.get('/api/user/')
        self.assertIn(
            "Authentication credentials were not provided.", str(response.data))
