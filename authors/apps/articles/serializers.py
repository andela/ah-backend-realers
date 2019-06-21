from rest_framework import serializers
from authors.apps.articles.models import Article,FavoriteAnArticle, LikeAnArticle
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

class FavoriteAnArticleSerializer(serializers.ModelSerializer):

    article = ArticleSerializer(required=False)
    favorited_by = UserSerializer(required=False)

    class Meta:
        fields = '__all__'
        model = FavoriteAnArticle
        read_only_fields = ['favorited_by', 'article']

class LikeAnArticleSerializer(serializers.ModelSerializer):

    article = ArticleSerializer(required=False)
    liked_by = UserSerializer(required=False)

    class Meta:
        fields = '__all__'
        model = LikeAnArticle
        read_only_fields = ['liked_by', 'article']
