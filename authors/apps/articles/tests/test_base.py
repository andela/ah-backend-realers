from authors.apps.authentication.tests.test_base import TestBase
from django.urls import reverse
from authors.apps.articles.models import Article


class ArticleBaseTest(TestBase):
    def setUp(self):
        self.article_url = reverse("articles:articles")
        super().setUp()

        self.article_data = {
            "article": {
                "title": "Most people are good",
                "description": "they are all good",
                "body": "is believed that most poeple love what tcbghfgx df",
                "image": "https://unsplash.com/photos/BW9ki_tmouE"
            }
        }

        self.article_data1 = {
            "article": {
                "title": "Most people are good",
                "description": "they are all gssood",
                "body": "It is what they sghf gvsdf csbkfdgc cbghfgx df",
                "image": "https://unsplash.com/photos/BW9ki_tmouE"
            }
        }

        self.new_db_article = Article(
            title="Most people are good",
            description="they are all good",
            body="It is believed that most poeple love what they sghf gvsdfdf",
            image="https://unsplash.com/photos/BW9ki_tmouE"

        )

        self.new_db_new_article = Article(
            title="Most people are good",
            description="they are all good",
            body="It is believed that most poeple and yes love what they sghf gvsdf csbkfdgc cbghfgx df",
            image="https://unsplash.com/photos/BW9ki_tmouE"

        )
        self.create_new_article = self.create_article()

    def create_article(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + str(self.token))
        response = self.client.post(
            self.article_url,
            data=self.article_data,
            format='json'
        )
        return response
