from django.test import TestCase
from authors.apps.articles.tests.test_base import ArticleBaseTest
from rest_framework import status

class ArticleTest(ArticleBaseTest):

    def test_create_article(self):
        self.assertEquals(self.create_new_article.status_code, status.HTTP_201_CREATED)

    def test_get_article(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(self.token))
        response = self.client.get(self.article_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_article(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(self.token))
        response = self.client.put(
            self.article_url + 'most-people-are-good/',
            data=self.article_data1,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_article_with_non_existant_article(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(self.token))
        response = self.client.put(
            self.article_url + 'most-people-are-good-awesome/',
            data=self.article_data1,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_article_with_no_permission(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(self.token1))
        response = self.client.put(
            self.article_url + 'most-people-are-good/',
            data=self.article_data1,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

