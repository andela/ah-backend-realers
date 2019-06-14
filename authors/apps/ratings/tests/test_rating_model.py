from authors.apps.authentication.tests.test_base import TestBase 
from authors.apps.ratings.tests.test_base import RatingsBaseTestCase
from ..models import Rating
from django.urls import reverse

class TestclassRating(RatingsBaseTestCase):

    def test_rating_object_return_rating(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(self.token))
        self.client.post(
            self.article_url,
            self.article_data_3,
            format='json'
        )

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(self.token1))
        rating_url = reverse(
            'ratings:rating',
            kwargs={'slug': "most-people"}
            )
        self.client.post(
                rating_url,
                data=self.rating_data,
                format='json'
            )

        rating = Rating.objects.first()
        self.assertEquals('1', str(rating))      
