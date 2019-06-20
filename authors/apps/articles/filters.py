from .models import Article
from django_filters import FilterSet, rest_framework


class ArticleFilter(FilterSet):
    title = rest_framework.CharFilter('title', lookup_expr='icontains')

    author = rest_framework.CharFilter(
        'author__username', lookup_expr='icontains')

    tagName = rest_framework.CharFilter(
        'tagName__tag_name', lookup_expr='icontains')

    class Meta:
        model = Article
        fields = ('title', 'author', 'tagName')
