from django.test import TestCase
from rest_framework import status
from .test_base import RatingsBaseTestCase
from django.urls import reverse


class TestRateArticle(RatingsBaseTestCase):
    def test_cannot_rate_your_own_article(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(self.token))
        article = self.create_dummy_article()

        rating_url = reverse(
            'ratings:rating',
            kwargs={'slug': article.get('data').get('slug')}
            )

        response = self.client.post(
                rating_url,
                data=self.rating_data,
                format='json'
            )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data.get('errors'), 'You cannot rate your own article')

    def test_already_rated_article(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(self.token))
        article = self.create_dummy_article()
        
        response = self.rate_article(article)
        response = self.rate_article(article)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('You have already rated this article', str(response.data))

    def test_article_doesnot_exist(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(self.token))
        rating_url = reverse(
            'ratings:rating',
            kwargs={'slug': 'does-not-exist'}
            )
        response = self.client.post(
            rating_url,
            data=self.rating_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('The article with that slug doesnot exist', response.data['errors'])

    def test_get_average_rating(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(self.token))
        article = self.create_dummy_article()

        response = self.rate_article(article)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        get_rating_url = reverse(
            'ratings:rating',
            kwargs={'slug': article.get('data').get('slug')}
            )
        response = self.client.get(get_rating_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('article').get('average_rating'), 1)

    def rate_article(self, article):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(self.token1))
        rating_url = reverse(
            'ratings:rating',
            kwargs={'slug': article.get('data').get('slug')}
            )

        response = self.client.post(
                rating_url,
                data=self.rating_data,
                format='json'
            )
        return response

    def test_article_ratings_doesnot_exist(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(self.token))
        rating_url = reverse(
            'ratings:rating',
            kwargs={'slug': 'does-not-exist'}
            )
        response = self.client.get(
            rating_url,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('Article doesnot exist', response.data['error'])


