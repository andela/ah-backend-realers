import json
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient


class UserRegistrationAPIViewTestCase(APITestCase):
    
    def setUp(self):
        self.client = APIClient()


    def test_user_registration(self):
        """
        Test to verify that a post call with user valid data
        """
        url = reverse("authentication:register")

        user_data = {
                    'user': {
                        'email': "test@testuser.com",
                        'username': "testuser",
                        'password': "password"
                    }
                } 

        response = self.client.post(url, user_data, format="json")
        result = json.loads(response.content)
        self.assertEquals(201, response.status_code)
        self.assertEqual("testuser", result['user']['username'])
