from rest_framework.pagination import LimitOffsetPagination


class ArticleSetPagination(LimitOffsetPagination):
    """set the number of articles to return on each page """
    default_limit = 10
    offset_query_param = 'offset'
 