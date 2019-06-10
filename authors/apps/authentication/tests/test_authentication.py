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

    def test_user_registration_with_invalid_credential(self):
        response = self.client.post(
            self.register_url, self.user_data_4, format='json'
        )
        email_error = "Email should not contain only numbers!"
        username_error = "Username should not contain only numbers!"
        password_error = "Password should not contain only numbers!"
        self.assertAlmostEquals(response.status_code, 400)
        self.assertIn(email_error, response.data['errors']['email'])
        self.assertIn(username_error, response.data['errors']['username'])
        self.assertIn(password_error, response.data['errors']['password'])

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

        response2 = self.client.post(
            self.url,
            {"user": {
                "email": "emmarealers.com",
                "password": "donthack"
            }},
            format="json")

        response3 = self.client.post(
            self.url,
            {"user": {
                "email": "emmarealers.com",
                "password": "dont-  hack"
            }},
            format="json")

        self.assertIn(
            'User with this email does not exist!',
            response.data["errors"]["email"]
        )

        self.assertIn(
            'Password should only contain letters and numbers',
            response3.data["errors"]["password"]
        )
        
        self.assertIn(
            "Please use a proper email format e.g janedoe@gmail.com",
            response2.data["errors"]["email"]
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response3.status_code, status.HTTP_400_BAD_REQUEST)


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
        self.assertIn("Token invalid or expired. please login again.", str(response.data))

    def test_fetch_user_from_system_with_no_token(self):
        response = self.client.get('/api/user/')
        self.assertIn("Authentication credentials were not provided.", str(response.data))

    def test_update_user_profile(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(self.token))
        response = self.client.put(
            '/api/user/',
            self.user_data_update,
            format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("test@testuser.com", response.data.get('email'))

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

class PasswordResetAPIViewTestCase(TestBase):
    """
    A test class that tests the PasswordResetView class in the views.py
    file 
    """

    def test_password_reset_with_valid_email_existing_in_app(self):
        #register test user into the app
        self.client.post(self.register_url, self.user_data_real_email, format="json") 
        url = reverse(
            "authentication:reset_password")
        response = self.client.post(url, self.user_data_real_email['user'], format="json")
        expected = "Please check your email inbox for the Password Reset link we've sent"
        self.assertEqual(expected, response.data['message'])

    def test_password_reset_with_valid_email_absent_in_app(self):
        url = reverse(
            "authentication:reset_password")
        response = self.client.post(url, self.user_data_real_email['user'], format="json")
        expected = "This Email Address is not attached to any account"
        self.assertEqual(expected, response.data['errors'][0])

    def test_password_reset_with_invalid_email(self):
        bad_email = {'email': "hgjfn"}
        url = reverse(
            "authentication:reset_password")
        response = self.client.post(url, bad_email, format="json")
        expected = "Provide a valid email address"
        self.assertEqual(expected, response.data['errors'][0])

    def test_password_reset_with_empty_email(self):
        bad_email = {'email': ""}
        url = reverse(
            "authentication:reset_password")
        response = self.client.post(url, bad_email, format="json")
        expected = "The email field can not be blank"
        self.assertEqual(expected, response.data['errors'][0])

    def test_password_reset_without_email_in_request(self):
        bad_email = {'d': "edfw"}
        url = reverse(
            "authentication:reset_password")
        response = self.client.post(url, bad_email, format="json")
        expected = "Please provide an Email Address"
        self.assertEqual(expected, response.data['errors'][0])

class CreateNewPasswordAPIViewTestCase(TestBase):
    """
    A test class that tests the CreateNewPasswordView class in the views.py
    file 
    """

    def test_create_new_password_good_request(self):
        #register test user into the app
        self.client.post(self.register_url, self.user_data_real_email, format="json")

        token = {
            "token": self.reset_token
        }
        url = reverse(
            "authentication:change_password", kwargs=token)
        response = self.client.patch(url, self.reset_data, format="json")
        expected = 'You have succesfully reset your password'
        self.assertEqual(expected, response.data['message'])

    def test_create_new_password_with_bad_token(self):
        #register test user into the app
        self.client.post(self.register_url, self.user_data_real_email, format="json")

        token = {
            "token": self.bad_reset_token
        }
        url = reverse(
            "authentication:change_password", kwargs=token)
        response = self.client.patch(url, self.reset_data, format="json")
        expected = 'This is an invalidated link'
        self.assertEqual(expected, response.data['errors'][0])

    def test_create_new_password_with_non_matching_passwords(self):
        #register test user into the app
        self.client.post(self.register_url, self.user_data_real_email, format="json")

        token = {
            "token": self.reset_token
        }
        url = reverse(
            "authentication:change_password", kwargs=token)
        response = self.client.patch(url, self.non_match_reset_data, format="json")
        expected = "Password is not macthing with Confirm_password!"
        self.assertEqual(expected, response.data['errors'][0])

    def test_create_new_password_with_less_characters(self):
        #register test user into the app
        self.client.post(self.register_url, self.user_data_real_email, format="json")

        token = {
            "token": self.reset_token
        }
        url = reverse(
            "authentication:change_password", kwargs=token)
        response = self.client.patch(url, self.less_password_chars, format="json")
        expected = "Password length must be 8 or more characters"
        self.assertEqual(expected, response.data['errors'][0])

    def test_create_new_password_with_an_empty_field(self):
        #register test user into the app
        self.client.post(self.register_url, self.user_data_real_email, format="json")

        token = {
            "token": self.reset_token
        }
        url = reverse(
            "authentication:change_password", kwargs=token)
        response = self.client.patch(url, self.one_empty_reset_data, format="json")
        expected = "Provide both Password and Confirm_Password fields"
        self.assertEqual(expected, response.data['errors'][0])

    def test_create_new_password_with_a_missing_field(self):
        #register test user into the app
        self.client.post(self.register_url, self.user_data_real_email, format="json")

        token = {
            "token": self.reset_token
        }
        url = reverse(
            "authentication:change_password", kwargs=token)
        response = self.client.patch(url, self.miss_field_reset_data, format="json")
        expected = "Provide both Password and Confirm_Password fields"
        self.assertEqual(expected, response.data['errors'][0])

    def test_create_new_password_with_a_length_less_than_8(self):
        #register test user into the app
        self.client.post(self.register_url, self.user_data_real_email, format="json")

        token = {
            "token": self.reset_token
        }
        url = reverse(
            "authentication:change_password", kwargs=token)
        response = self.client.patch(url, self.with_invalid_length, format="json")
        expected = "Password length must be 8 or more characters"
        self.assertEqual(expected, response.data['errors'][0])