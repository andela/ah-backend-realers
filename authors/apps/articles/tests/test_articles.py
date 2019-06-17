from django.test import TestCase
from authors.apps.articles.tests.test_base import ArticleBaseTest
from rest_framework import status

class ArticleTest(ArticleBaseTest):

    def test_create_article(self):
        self.assertEquals(self.create_new_article.status_code, status.HTTP_201_CREATED)

    def test_create_article_with_existing_body(self):
        response = self.client.post(
            self.article_url,
            self.article_data,
            format='json'
        )
        self.assertIn('Article with this body already exists!', str(response.data))

    def test_get_article(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(self.token))
        
        response = self.client.get(self.article_url)
        slug = self.create_new_article.data["data"]["slug"]
        response2 = self.client.get(self.article_url+f"{slug}/")
        response3 = self.client.get(self.article_url+f"{slug}y/")
        
        self.assertEqual(response3.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)

    def test_delete_article(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(self.token))
        
        slug = self.create_new_article.data["data"]["slug"]
        response = self.client.delete(self.article_url+f"{slug}/")
        response2 = self.client.delete(self.article_url+f"{slug}df/")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response2.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("success", response.data)

    def test_update_article(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(self.token))
        response = self.client.patch(
            self.article_url + 'most-people-are-good/',
            data=self.article_data2,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_article_with_non_existant_article(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(self.token))
        response = self.client.patch(
            self.article_url + 'most-people-are-good-awesome/',
            data=self.article_data1,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_update_article_with_no_permission(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(self.token1))
        response = self.client.patch(
            self.article_url + 'most-people-are-good/',
            data=self.article_data1,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_article_without_permission(self):
        self.client.credentials()
        response = self.client.patch(
            self.article_url + 'most-people-are-good/',
            data=self.article_data1,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_article_fails_with_bad_request_body(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(self.token))
        response = self.client.patch(
            self.article_url + 'most-people-are-good/',
            data=self.wrong_request_body,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)