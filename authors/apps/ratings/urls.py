from django.urls import path
from .views import ArticleRating

urlpatterns = [
    path('articles/<slug>/rating/', ArticleRating.as_view(), name="rating")
]
