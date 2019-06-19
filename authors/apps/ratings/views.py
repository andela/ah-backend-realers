from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import status
from .models import User
from rest_framework.permissions import IsAuthenticated
from .serializers import RatingSerializers
from rest_framework.exceptions import NotFound
from authors.apps.articles.models import Article
from authors.apps.articles.serializers import ArticleSerializer
from authors.apps.ratings.models import Rating
from rest_framework.response import Response
from django.db.models import Avg
from drf_yasg.utils import swagger_auto_schema

class ArticleRating(APIView):
    serializer_class = RatingSerializers
    article_serializer_class = ArticleSerializer
    Permission_classes = (IsAuthenticated,)
    queryset = Rating.objects.all()

    @swagger_auto_schema(
        operation_description='Rating an article.',
        operation_id='rate an article',
        request_body=serializer_class,
        responses={201: serializer_class(many=False), 400: 'BAD REQUEST'},
    )

    def post(self, request, **kwargs):
        article = Article.objects.filter(slug=self.kwargs['slug']).first()

        if not article:
            return Response(
                {
                    "errors": "The article with that slug doesnot exist"
                },
                status=status.HTTP_404_NOT_FOUND
                )
          
        # check if the owner of the article does not rate their own
        if article.author == request.user:
            return Response(
                {
                    "errors": "You cannot rate your own article"
                },
                status=status.HTTP_403_FORBIDDEN
                )
        
        rating = request.data.get('ratings')
        data = {
            "ratings": rating,
            "username": request.user.username
        }
        serializers = RatingSerializers(data=data)
        serializers.is_valid(raise_exception=True)

        article_rating = Rating.objects.filter(
            article_id=article.id, username=request.user.username).first()

        if article_rating:
            return Response({
                "message": "You have already rated this article"
            })
        else:
            serializers.save(article=article)
            return Response({
                "ratings": serializers.data
            }, status=status.HTTP_201_CREATED)

    def get(self, request, **kwargs):
        """ gets average of a single article rating"""
        article = Article.objects.filter(slug=self.kwargs['slug']).first()
        if article:
            serializer = self.article_serializer_class(article, partial=True)
            return Response({
                "article": serializer.data,
            }, status.HTTP_200_OK)

        return Response(
            {"error": "Article doesnot exist"}, status=status.HTTP_404_NOT_FOUND)
