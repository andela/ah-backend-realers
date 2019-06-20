from django.db import models
from authors.apps.authentication.models import User
from django.utils import text
from rest_framework.response import Response
from django.db.models import Avg
from authors.apps.article_tagging.models import ArticleTagging


class Article(models.Model):
    title = models.CharField(db_index=True, max_length=255)
    description = models.TextField()
    body = models.TextField(unique=True)
    createdAt = models.DateTimeField(auto_now_add=True, editable=False)
    updatedAt = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='author')
    slug = models.SlugField()
    image = models.URLField(blank=True, default='url', max_length=200)
    tagName = models.ManyToManyField(
        ArticleTagging, related_name="articles", blank=True
    )

    def slug_generator(self):
        num = 1
        slug_genereted = text.slugify(self.title)
        while Article.objects.filter(slug=slug_genereted).exists():
            slug_genereted = '{}-{}'.format(slug_genereted, str(num))
            num += 1
        return slug_genereted

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.slug_generator()
        super(Article, self).save(*args, **kwargs)

    def __str__(self):
        return self.title

    def average_rating(self):
        from authors.apps.ratings.models import Rating

        article = Article.objects.filter(id=self.id).first()
        if article:
            queryset = Rating.objects.all().filter(
                article_id=article.id)
            if queryset.exists():
                article_average = queryset.aggregate(Avg('ratings'))
                rating = article_average.get('ratings__avg')
                return rating
        return 0
class FavoriteAnArticle(models.Model):

    is_favorited = models.BooleanField(default=False)
    favorited_by = models.ForeignKey(User, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
