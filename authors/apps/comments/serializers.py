from rest_framework import serializers

from authors.apps.articles.models import Article
from authors.apps.authentication.serializers import UserSerializer
from .models import Comment

class RecursiveField(serializers.Serializer):
    def to_presentation(self, instance):
        serializer = self.parent.parent.__class__(
            instance,
            context=self.context
        )
        return serializer.data


class CommentSerializer(serializers.ModelSerializer):
    children = RecursiveField(required=False, many=True)
    parent = serializers.SerializerMethodField
    author = UserSerializer(read_only=True)
    article = serializers.StringRelatedField(many=False)

    class Meta:
        model = Comment
        fields = (
            'id',
            'body',
            'article',
            'parent',
            'created_on',
            'updated_on',
            'author',
            'children',
        )

    def create(self, validated_data):
        author = self.context.get("author")
        article = self.context.get("article")
        comment = Comment.objects.create(author=author, article=article, **validated_data)
        return comment