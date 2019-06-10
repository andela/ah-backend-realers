from .test_base import TestBase
import json
from rest_framework import status
from django.urls import reverse


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

    def test_Validate_email_invalid(self):
        result = self.new_user
        expected = "Enter a valid email address."
        self.assertEqual(expected, result.data['errors']['email'][0])

    def test_email_already_exists(self):
        result = self.client.post(
            self.register_url, self.user_data12, format="json")
        expected = "User with this email already exists"
        self.assertEqual(expected, result.data['errors']['email'][0])

    def test_invalid_password(self):
        response = self.new_user2
        expected = "Password should contain atleast 8 characters"
        self.assertIn(expected, response.data['errors']['password'][0])

    def test_password_empty(self):
        response = self.new_users2
        expected = "This field may not be blank"
        self.assertIn(expected, response.data['errors']['password'][0])

    def test_validate_username_exist(self):
        response = self.client.post(
            self.register_url, self.user_data11, format="json")
        expected = "Username already exists"
        self.assertIn(expected, response.data['errors']['username'][0])

    def test_username_has_special_characters(self):
        response = self.new_users
        expected = "username should only contain letters and numbers"
        self.assertIn(expected, response.data['errors']['username'])


class UserLoginAPIViewTestCase(TestBase):
    """ 
    Test to test the loginAPIView in the views file.
    """

    def test_login_for_signed_up_user(self):
        self.assertEquals("test@testuser.com", self.logged_in_user.data["email"])
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
        self.assertIn("Authentication credentials were not provided.", str(response.data))


class AccountActivationAPIViewTestCase(TestBase):
    """
    A test class that tests the AccountActivationAPIViewTestCase class in the views
    file 
    """

    def test_account_verification_with_valid_key(self):
        token = {
            "token": self.known_key
        }
        url = reverse(
            "authentication:acc_verification", kwargs=token)

        response = self.client.get(url)
        expected = "User with email {} has been activated".format(
            self.user_data_2['user']['email'])
        self.assertEqual(expected, response.data)

    def test_account_verification_with_invalid_key(self):
        token = {
            "token": self.invalid_key
        }
        url = reverse(
            "authentication:acc_verification", kwargs=token)

        response = self.client.get(url)

        self.assertEqual("Account doesn't exist", response.data)

