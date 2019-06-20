from rest_framework import serializers
from authors.apps.articles.models import Article,FavoriteAnArticle
from authors.apps.authentication.serializers import UserSerializer
import re

from .validators import validate_body, check_title, check_desription
from authors.apps.article_tagging.models import ArticleTagging

class ArticleSerializer(serializers.ModelSerializer):
    author = UserSerializer(required=False)
    slug = serializers.CharField(read_only=True)
    image = serializers.URLField(allow_blank=True, required=False)
    title = serializers.CharField(validators=[check_title])
    body = serializers.CharField(validators=[validate_body])
    description = serializers.CharField(validators=[check_desription])
    tagName = serializers.SlugRelatedField(
        many=True,
        queryset=ArticleTagging.objects.all(),
        slug_field='tag_name',
        required=False
    )

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
            'average_rating',
            'tagName',
        ]

class FavoriteAnArticleSerializer(serializers.ModelSerializer):

    article = ArticleSerializer(required=False)
    favorited_by = UserSerializer(required=False)

    class Meta:
        fields = '__all__'
        model = FavoriteAnArticle
        read_only_fields = ['favorited_by', 'article']
