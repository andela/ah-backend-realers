from .test_base import TestBase
import json
from rest_framework import status

class UserRegistrationAPIViewTestCase(TestBase):   

    def test_user_registration(self):
        """
        Test to verify that a post call with user valid data
        """

        result = json.loads(self.new_test_user.content)
        self.assertEquals(201, self.new_test_user.status_code)
        self.assertEqual("testuser", result['user']['username'])


class UserLoginAPIViewTestCase(TestBase):
    """ 
    Test to test the loginAPIView in the views file.
    """

    def test_login_for_signed_up_user(self):
        
        self.assertEquals("test@testuser.com", self.logged_in_user.data["email"])
        self.assertEqual(self.logged_in_user.status_code , status.HTTP_200_OK)

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

    def test_fetch_user_from_system(self):

        self.client.login(
            email=self.user_data['user']['email'], password=self.user_data['user']['password'])
        response = self.client.get(
            # unlike other routes this has no key name
            # touse to refer to it in the urls file
            '/api/user/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

