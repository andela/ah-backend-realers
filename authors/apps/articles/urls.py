from django.urls import path, include
from .views import ArticleView, ArticleRetrieveUpdateDestroy

urlpatterns = [
    path('articles/', ArticleView.as_view(), name="articles"),
    path('articles/<str:slug>/', ArticleRetrieveUpdateDestroy.as_view(), name="slug"),
    path('articles/', include(('authors.apps.comments.urls', 'comments'), namespace='comments')),
]