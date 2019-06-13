from django.db import models
from authors.apps.authentication.models import User
from django.utils import text

class Article(models.Model):
    title = models.CharField(db_index=True, max_length=255)
    description = models.TextField()
    body = models.TextField(unique=True)
    createdAt = models.DateTimeField(auto_now_add=True, editable=False)
    updatedAt = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='author')
    slug = models.SlugField()
    image = models.URLField(blank=True, default='url', max_length=200)

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