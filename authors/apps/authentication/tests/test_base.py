from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from ..models import User
import json

class TestBase(APITestCase):
    
    def setUp(self):
        self.client = APIClient()
        self.url = reverse("authentication:login")
        self.register_url = reverse("authentication:register") 

        self.user_data = {
                'user': {
                    'email': "test@testuser.com",
                    'username': "testuser",
                    'password': "password",
                    'bio': "I am test user",
                    'image': "image-link"
                    }
                }
       
        self.new_test_user = self.client.post(
            self.register_url, self.user_data, format="json")                             
        
        # use the APIClient to log in the user to be tested against
        self.logged_in_user = self.client.post(
            self.url, self.user_data, format="json")

        #individualise these to easily test against them
        self.username = "neelxie" 
        self.email = "derek@derek.com"
        self.password = "realers"

        #create user for models tests
        self.new_db_user = User( 
            email=self.email, 
            password=self.password,
            username=self.username)

        #Getting the token
        self.token = self.logged_in_user.data.get("token")
