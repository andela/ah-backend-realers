from django.urls import reverse
from rest_framework.test import APIClient, APITestCase
from authors.apps.authentication.tests.test_base import TestBase 


class RatingsBaseTestCase(TestBase):
    def setUp(self):
        super().setUp()

        self.article_url = reverse("articles:articles")

        # user rates an article
        self.rating_data = {
            "ratings": 1
        }

        # returned data when getting article
        self.article_average_rating = {
            "average": {
                "article_rating": 3.3333333333333335,
                "article": "we-eat"
            }
        }

        self.article_not_found = {
            "article": {
                "title": "Most people1234 are good",
                "description": "they1234 are all good",
            }
        }

        self.article_data = {
            "article": {
                "title": "Most people are good",
                "description": "they are all good",
                "body": "is believed that most poeple love what tcbghfgx df",
                "image": "https://unsplash.com/photos/BW9ki_tmouE"
            }
        }

        self.article_data_3 = {
            "article": {
                "title": "Most people",
                "description": "they is all good",
                "body": "is believed that most poeple love what tcbghfgx df",
                "image": "https://unsplash.com/photos/BW9ki_tmouE"
            }
        }

    def create_dummy_article(self):
        response = self.client.post(
            self.article_url,
            self.article_data,
            format='json'
        )
        return response.data
