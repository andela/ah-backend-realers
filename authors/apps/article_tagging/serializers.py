from rest_framework.serializers import (ModelSerializer,
                                        SlugRelatedField, )
from authors.apps.articles.models import Article
from authors.apps.article_tagging.models import ArticleTagging

class ArticleTaggingSerializer(ModelSerializer):
    articles = SlugRelatedField(
        many=True,
        slug_field='slug',
        read_only=True
    )

    class Meta:
        model = ArticleTagging
        fields = ('tag_name','articles')
