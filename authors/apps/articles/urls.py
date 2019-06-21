from django.urls import path, include
from .views import (ArticleView, ArticleRetrieveUpdateDestroy,
                    FavoriteUnfavoriteAnArticle, UserFavouriteArticles,
                    LikeUnlikeAnArticle, UserLikedArticles)

urlpatterns = [
    path('articles/', ArticleView.as_view(), name="articles"),
    path('articles/<str:slug>/', ArticleRetrieveUpdateDestroy.as_view(), name="slug"),
    path('articles/', include(('authors.apps.comments.urls', 'comments'), namespace='comments')),
    path('articles/<str:slug>/favorite/',
         FavoriteUnfavoriteAnArticle.as_view(), name='favorite'),
    path('favorite-articles/', UserFavouriteArticles.as_view(),
         name="favorite_articles"),
    path('articles/<slug:slug>/like/',
         LikeUnlikeAnArticle.as_view(), name='like'),
    path('liked-articles/', UserLikedArticles.as_view(),
         name="liked_articles"),
]
