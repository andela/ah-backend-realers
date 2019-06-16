from django.urls import path, include
from .views import (ArticleView, ArticleRetrieveUpdateDestroy,
                    FavoriteUnfavoriteAnArticle, UserFavouriteArticles)

urlpatterns = [
    path('articles/', ArticleView.as_view(), name="articles"),
    path('articles/<str:slug>/', ArticleRetrieveUpdateDestroy.as_view(), name="slug"),
    path('articles/', include(('authors.apps.comments.urls', 'comments'), namespace='comments')),
    path('articles/<str:slug>/favorite/',
         FavoriteUnfavoriteAnArticle.as_view(), name='favorite'),
    path('favorite-articles/', UserFavouriteArticles.as_view(),
         name="favorite_articles"),
]
