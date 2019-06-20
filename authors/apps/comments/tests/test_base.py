from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
import json, os
from ..views import CommentAPIView, ManageCommentAPIView
from authors.apps.authentication.backends import AccountVerification


class TestBase(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.url = reverse("authentication:login")
        self.register_url = reverse("authentication:register")
        self.acc_verify = AccountVerification
        self.article_url = reverse("articles:articles")

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

        # verifies the two users accounts upon signup
        self.acc_verify.verify_user(self.user_data['user']['email'])
        self.acc_verify.verify_user(self.user_data_2['user']['email'])

        # use the APIClient to log in the users
        self.log_in_user = self.client.post(
            self.url, self.user_data, format="json")
        self.log_in_user2 = self.client.post(
            self.url, self.user_data_2, format="json")

        # Getting the tokens
        self.token1 = self.log_in_user.data.get("token")
        self.token2 = self.log_in_user2.data.get("token")

        #Good comment data
        self.comment_data = {
            'comment': {
                'body': "we dem' boys, Holla"
            }
        }

        #Request data missing comment
        self.request_data_no_comment = {
            'not_comment': {
                'body': "we dem' boys, Holla"
            }
        }

        #Comment data missing body
        self.comment_data_no_body = {
            'comment': {
                'not_body': "we dem' boys, Holla"
            }
        }

        #Article data to create test articles
        self.article_data = {
            "article": {
                "title": "kings",
                "description": "they are fly",
                "body": "It is what they do",
                "image": "https://unsplash.com/",
                "tagName":["people", "love"]
            }
        }

        self.article_data2 = {
            "article": {
                "title": "kingss",
                "description": "they are flying",
                "body": "It is what they do it",
                "image": "https://unsplashf.com/",
                "tagName":["people", "love"]
            }
        }

        #Post test articles using new_test_user and get it's slug
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(self.token1))
        self.article = self.client.post(
            self.article_url,
            data=self.article_data,
            format="json"
            )
        self.article_slug = self.article.data["data"]["slug"]

        self.article2 = self.client.post(
            self.article_url,
            data=self.article_data2,
            format="json"
            )
        self.article_slug2 = self.article2.data["data"]["slug"]

        # post test comment
        self.create_url = self.article_url+f"{self.article_slug}/comments/"
        response = self.client.post(
            self.create_url,
            data=self.comment_data,
            format='json'
            )
        self.comment_id = response.data['comment']['id']  


