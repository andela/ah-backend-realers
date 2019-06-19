from django.db import models

from mptt.models import MPTTModel, TreeForeignKey
from authors.apps.authentication.models import User

from authors.apps.articles.models import Article


class Comment(MPTTModel):

    body = models.TextField()

    article = models.ForeignKey(
        Article,
        related_name='comments',
        on_delete=models.CASCADE)

    author = models.ForeignKey(
        User,
        related_name='comments',
        on_delete=models.CASCADE)

    parent = TreeForeignKey(
        'self',
        null=True,
        blank=True,
        related_name='children',
        db_index=True,
        on_delete=models.CASCADE
    )

    created_on = models.DateTimeField(auto_now_add=True)

    updated_on = models.DateTimeField(auto_now=True)

    class MPTTMeta:
        order_insertion_by = ['created_on']

    def __str__(self):
        return self.body