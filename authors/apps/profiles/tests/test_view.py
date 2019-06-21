from .test_base import ProfileTestBase
import json
from rest_framework import status
from django.urls import reverse
from ..exceptions import ProfileDoesNotExist


class UpdateGetUserProfileAPIViewTestCase(ProfileTestBase):
    """
    A test class that tests the UpdateGetUserProfileAPIView class in the views
    file 
    """

    def test_retrieve_user_profile(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(self.token))
        response = self.client.get(
            # unlike other routes this has no key name
            # to use to refer to it in the urls file
            '/api/profiles/testuser/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('username'), 'testuser')

    def test_retrieve_user_profile_fails_with_inexist_user(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(self.token))

        response = self.client.get('/api/profiles/testuserb/')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        errors = response.data.get('errors')
        self.assertEqual(errors.get('detail'),
                         'The requested user profile does not exist.')

    def test_unauthenticated_user_cannot_retrieve_profile(self):
        response = self.client.get(
            "/api/profiles/{}/".format("alexxsanya"), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_profile_successfully(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(self.token))
        response = self.client.patch(
            "/api/profiles/{}/".format("testuser"),
            data=json.dumps(self.valid_user_profile),
            content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("bio"),
                         self.valid_user_profile["profile"]["bio"])

    def test_update_fails_with_invalid_firstname(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(self.token))
        response = self.client.patch(
            "/api/profiles/{}/".format("testuser"),
            data=json.dumps(self.profile_invalid_firstname),
            content_type='application/json') 
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_fails_with_invalid_lastname(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(self.token))
        response = self.client.patch(
            "/api/profiles/{}/".format("testuser"),
            data=json.dumps(self.profile_invalid_lastname),
            content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_user_cant_update_another_users_profile(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(self.token))
        response = self.client.patch(
            "/api/profiles/{}/".format("testuser2"),
            data=json.dumps(self.valid_user_profile),
            content_type="application/json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_update_profile_of_inexistent_user(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(self.token))
        response = self.client.patch(
                                     "/api/profiles/{}/".format("alexxsanya"),
                                     data=json.dumps(self.valid_user_profile),
                                        content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)