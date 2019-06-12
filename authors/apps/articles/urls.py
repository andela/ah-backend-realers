from django.urls import path
from .views import ArticleView, ArticleRetrieveUpdateDestroy

urlpatterns = [
    path('articles/', ArticleView.as_view(), name="articles"),
    path('articles/<str:slug>/', ArticleRetrieveUpdateDestroy.as_view(), name="slug"),
]