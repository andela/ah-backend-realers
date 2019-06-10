from unittest.mock import patch, Mock
from django.urls import reverse
from rest_framework.views import status
from rest_framework.test import APITestCase, APIClient


class TestSocialAuthentication(APITestCase):
    """
    This class is to test the social authentication 
    feature for facebook, twitter and google.
    """

    def setUp(self):

        # get the various urls to test against
        self.facebook_url = reverse("authentication:auth-facebook")
        self.google_url = reverse("authentication:auth-google")
        self.twitter_url = reverse("authentication:auth-twitter")

        # test client
        self.client = APIClient()
        self.correct_facebook_token = {
            "access_token": "JleHAiOjE1NjI5MzEzODQsImlhdCI6MTU2MDMzOTM4NCwia"
        }
        self.fake_access_token = {
            "access_token": "my_fake_access_token"
        }
        self.google_token = {
            "access_token": "google_auth_token"
        }
        self.twitter_token = {
            "access_token": "realers_the_team_ever",
            "access_token_secret": "ono_code_alumya_enjala"
        }

    @patch('google.oauth2.id_token.verify_oauth2_token')
    def test_google_authentication_user_registration(self, google_user_details):
        """
        This mocks the google authentication registration
        """
        google_user_details.return_value = {
            "email": "realers@derek.com",
            "name": "ngankooye"
        }
        response = self.client.post(
            self.google_url, self.google_token, format="json")
        self.assertEqual(
            response.status_code, status.HTTP_200_OK)

    @patch('google.oauth2.id_token.verify_oauth2_token')
    def test_google_socio_authentication_user_login(self, google_login_obj):
        """
        Mocking test for google login authentication
        """
        google_login_obj.return_value = {
            "email": "realers@derek.com",
            "name": "ngankooye"
        }
        self.client.post(
            self.google_url, self.google_token, format="json")
        response = self.client.post(
            self.google_url, self.google_token, format="json")
        self.assertEqual(
            response.status_code, status.HTTP_200_OK)

    @patch('facebook.GraphAPI.get_object')
    def test_facebook_socio_authentication_registration(self, facebook_user_object):
        """
        Test to mock facebook authentication registration
        """
        facebook_user_object.return_value = {
            "email": "derek@toorich.com",
            "name": "quality"
        }
        response = self.client.post(
            self.facebook_url, self.correct_facebook_token, format="json")
        self.assertEqual(
            response.status_code, status.HTTP_200_OK)

    @patch('facebook.GraphAPI.get_object')
    def test_facebook_socio_authentication_login(self, login_facebook_obj):
        """
        Mocking test for google login authentication
        """
        login_facebook_obj.return_value = {
            "email": "derek@toorich.com",
            "name": "quality"
        }
        self.client.post(
            self.facebook_url, self.correct_facebook_token, format="json")
        response = self.client.post(
            self.facebook_url, self.correct_facebook_token, format="json")
        self.assertEqual(
            response.status_code, status.HTTP_200_OK)
    
    @patch('facebook.GraphAPI.get_object')
    def test_facebook_authentication_fake_token(self, fake_token):
        """
        Test fake facebook authentication login
        """
        self.client.post(self.facebook_url, self.correct_facebook_token,
                         format="json")
        response = self.client.post(self.facebook_url,
                                    self.fake_access_token, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    @patch('twitter.Api.VerifyCredentials')
    def test_twitter_authentication_fake_token(self, derrick_info):
        """
        Twitter test with fake facebook authentication token
        """
        self.client.post(self.twitter_url, self.twitter_token,
                         format="json")
        response = self.client.post(self.twitter_url,
                                    self.fake_access_token, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('google.oauth2.id_token.verify_oauth2_token')
    def test_google_authentication_fake_token(self, un_need_ed):
        """
        Test authentication login for google with fake token
        """
        self.client.post(self.google_url, self.google_token,
                         format="json")
        response = self.client.post(self.google_url,
                                    self.fake_access_token, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    