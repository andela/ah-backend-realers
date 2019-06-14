from authors.apps.articles.tests.test_base import ArticleBaseTest
from authors.apps.articles.models import Article
from authors.apps.authentication.models import User
from authors.apps.ratings.tests import test_base
from rest_framework import status
from django.urls import reverse


class ArticleModelTest(ArticleBaseTest):
    def test_slug_generator(self):
        user = User.objects.first()
        self.new_db_article.author = user
        self.new_db_article.save()
        self.new_db_new_article.author = user
        self.new_db_new_article.save()
        self.assertTrue(self.new_db_new_article)

    def test_object_returns_article_title(self):
        article = Article.objects.first()
        self.assertIn('Most people are good', str(article))

    
    def test_get_average_rating(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(self.token))
        article = self.create_new_dummy_article()
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
