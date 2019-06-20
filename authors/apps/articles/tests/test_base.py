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
                "image": "https://unsplash.com/photos/BW9ki_tmouE",
                "tagName":["people", "love"]
            }
        }

        self.article_data22 = {
            "article": {
                "title": "l love food",
                "description": "they all like food",
                "body": "l like eating well",
                "image": "https://unsplash.com/photos/BW9ki_tmouE",
                "tagName":["people", "love"]
            }
        }

        self.article_data1 = {
            "article": {
                "title": "Most people are good",
                "description": "they are all gssood",
                "body": "It is what they sghf gvsdf csbkfdgc cbghfgx df",
                "image": "https://unsplash.com/photos/BW9ki_tmouE",
                "tagName":["people","love"]
            }
        }
        self.article_no_tag = {
            "article": {
                "title": "no tags",
                "description": "I have no tags",
                "body": "I am an article with no tags",
                "image": "https://unsplash.com/photos/BW9ki_tmouE",
            }
        }

        self.article_data2 = {
            "article": {
                "description": "all is good",
                "tagName":["people", "love"]
            }
        }
        
        self.wrong_request_body = {
             "title": "Most people are good",
            "description": "they are all gssood",
            "body": "It is what they sghf gvsdf csbkfdgc cbghfgx df",
            "image": "https://unsplash.com/photos/BW9ki_tmouE"            
        }

        self.rating_data = {
            "ratings": 1
        }

        self.new_db_article = Article(
            id=int(90),
            title="Most people are good",
            description="they are all good",
            body="It is believed that most poeple love what they sghf gvsdfdf",
            image="https://unsplash.com/photos/BW9ki_tmouE",
        )
        self.new_db_article.tagName.articles = ["people"]

        self.new_db_new_article = Article(
            id=int(89),
            title="Most people are good",
            description="they are all good",
            body="It is believed that most poeple and yes love what they sghf gvsdf csbkfdgc cbghfgx df",
            image="https://unsplash.com/photos/BW9ki_tmouE"
        )
        self.new_db_new_article.tagName.articles = ["people"]

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

    def create_dummy_article(self):
        response = self.client.post(
            self.article_url,
            self.article_data,
            format='json'
        )
        return response.data

    def create_new_dummy_article(self):
        response = self.client.post(
            self.article_url,
            self.article_data22,
            format='json'
        )
        return response.data

        