from authors.apps.articles.tests.test_base import ArticleBaseTest
from authors.apps.articles.models import Article
from authors.apps.authentication.models import User

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