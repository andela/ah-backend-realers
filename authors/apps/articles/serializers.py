from rest_framework import serializers
from authors.apps.articles.models import Article
from authors.apps.authentication.serializers import UserSerializer
import re


class ArticleSerializer(serializers.ModelSerializer):
    author = UserSerializer(required=False)
    slug = serializers.CharField(read_only=True)
    image = serializers.URLField(allow_blank=True, required=False)
    title = serializers.CharField(required=True)
    body = serializers.CharField(required=True)
    body = serializers.CharField(required=True)

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
            'image'
        ]

    def validate(self, data):
        fieldzo = [data['title'], data['body'], data['description']]
        for field in fieldzo:
            if field.isnumeric() or type(field) == int:
                raise serializers.ValidationError(
                    "One of the inputs is a numbers. Please verify it"
                )
        return data
