from django.db import models
from authors.apps.authentication.models import User
from authors.apps.articles.models import Article
# Create your models here.


class Rating(models.Model):
    article = models.ForeignKey(Article, related_name='articles',
                                on_delete=models.CASCADE)
    username = models.ForeignKey(User, to_field='username',
                             on_delete=models.CASCADE, null=False)
    ratings = models.IntegerField(null=False, default=0)

    def __str__(self):
        return str(self.ratings)
