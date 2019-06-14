from rest_framework import serializers
from authors.apps.articles.models import Article
from authors.apps.authentication.serializers import UserSerializer
import re

from .validators import validate_body, check_title, check_desription

class ArticleSerializer(serializers.ModelSerializer):
    author = UserSerializer(required=False)
    slug = serializers.CharField(read_only=True)
    image = serializers.URLField(allow_blank=True, required=False)
    title = serializers.CharField(validators=[check_title])
    body = serializers.CharField(validators=[validate_body])
    description = serializers.CharField(validators=[check_desription])

    class Meta:
        model = Article
        fields = [
            'title',
            'description',
            'body',
            'createdAt',
            'updatedAt',
            'author',
            'slug',
            'image',
            'average_rating'
        ]
        