from django.shortcuts import render
from rest_framework.generics import (
    ListCreateAPIView, RetrieveUpdateDestroyAPIView, CreateAPIView, DestroyAPIView, RetrieveAPIView)
from rest_framework import status,exceptions
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from .serializers import ArticleSerializer, FavoriteAnArticleSerializer, LikeAnArticleSerializer
from .models import Article, FavoriteAnArticle, LikeAnArticle
from authors.apps.authentication.models import User
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from django.shortcuts import get_object_or_404,get_list_or_404
import json 
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import PermissionDenied
from .pagination import ArticleSetPagination


class ArticleView(ListCreateAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = ArticleSetPagination

    def post(self, request):
        article = request.data.get("article", {})

        serializer = self.serializer_class(data=article)
        serializer.is_valid(raise_exception=True)
        serializer.save(
            author=User.objects.filter(username=request.user.username).first()
        )
        response = {
            "success": "Article successfully created!", 
            "data": serializer.data
            }
        return Response(response, status=status.HTTP_201_CREATED)


class ArticleRetrieveUpdateDestroy(RetrieveUpdateDestroyAPIView):
    serializer_class = ArticleSerializer
    permission_class = AllowAny
    queryset = Article.objects.all()
    lookup_field = 'slug'

    def get(self, request, **kwargs):
        article = Article.objects.filter(slug=kwargs.get('slug')).first()
        if not article:
            return Response({
                "message": "Article does not exist",
                "status":status.HTTP_404_NOT_FOUND
            }, status.HTTP_404_NOT_FOUND)
        try:
            favorited = FavoriteAnArticle.objects.get(article__id=article.id)
            serializer = FavoriteAnArticleSerializer(
                favorited,
                partial=True
            )
        except ObjectDoesNotExist:
            serializer = self.serializer_class(
                article,
                partial=True
            )
        
        response = {
            "message":"article successful retrieved",
            "data":serializer.data,
            "status":status.HTTP_200_OK
        }
        return Response(response, status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        is_authenticated(request)
        article = Article.objects.filter(slug=kwargs.get('slug')).first()
        if not article:
            return Response({
                "message": "Article does not exist"
            }, status.HTTP_404_NOT_FOUND)
        if request.user.username != article.author.username:
            return Response({
                "message": "You do not have permision to update this article"
            }, status.HTTP_401_UNAUTHORIZED)

        article_data = request.data.get("article", {})
        if article_data:
            serializer = self.serializer_class(
                article,
                data=article_data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            response = {"success": "Article successfully updated!",
                        "data": serializer.data}
            return Response(response, status.HTTP_200_OK)
        return Response({
            "message": "Please use proper request body!",
            "status": status.HTTP_400_BAD_REQUEST
        }, status.HTTP_400_BAD_REQUEST)


    def delete(self, request, **kwargs):
        is_authenticated(request)
        article = Article.objects.filter(slug=kwargs.get('slug')).first()
        if not article:
            return Response({
                "message": "Article does not exist"
            }, status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(
            article,
            partial=True
        )
        article.delete()
        response = {
            "success": "Article successfully deleted!", 
            "article": serializer.data
            }
        return Response(response, status.HTTP_200_OK)


def is_authenticated(request):
    user = request.user.id

    if user == None:
        raise PermissionDenied({
            "message": "Please Login to proceed",
            "status": status.HTTP_403_FORBIDDEN
        })

class FavoriteUnfavoriteAnArticle(CreateAPIView, DestroyAPIView):
    """If the user feels satisfied with the article, he can favourite it """

    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = FavoriteAnArticle.objects.all()
    serializer_class = FavoriteAnArticleSerializer
    article_serializer_class = ArticleSerializer

    def check_article_exists(self, **kwargs):
        """
        Check whether the article with specified slug exists
        """
        try:
            article = get_object_or_404(Article, slug=kwargs.get("slug"))
            return article
        except:
            raise exceptions.ValidationError({"message": "Article doesn't exit"})

    @swagger_auto_schema(
        operation_description='Favorite an Article.',
        operation_id='favorite an article',
        responses={200: serializer_class(many=False), 400: 'BAD REQUEST'},
    )
    def post(self, request, **kwargs):
        """
        Favorite an article with specified slug
        """
        message =  "You favorited this article already"
        article = self.check_article_exists(**kwargs)
        favorite = FavoriteAnArticle.objects.filter(
            favorited_by=request.user, article=article
        )
        if not favorite:
            serializer = self.serializer_class(data={"is_favorited": True})
            serializer.is_valid(raise_exception=True)
            serializer.save(article=article, favorited_by=request.user)

            message = "You have favorited this article successfully"
        return Response(
            {
                "message": message,
                "status": status.HTTP_200_OK,
                "data": {
                    "article": {
                        "title": str(article)
                    }
                }
            },
            status=status.HTTP_200_OK,
        )

    @swagger_auto_schema(
        operation_description='Unfavorite an Article.',
        operation_id='unfavorite an article',
        request_body=None,
        responses={200: serializer_class(many=False), 400: 'BAD REQUEST'},
    )
    def delete(self, request, **kwargs):
        """
        Unfavorite an article
        """
        queryset = FavoriteAnArticle.objects.filter(favorited_by=request.user)
        article = self.check_article_exists(**kwargs)
        message = "You have not favorited this article yet"
        status_code = status.HTTP_400_BAD_REQUEST
        favorited_article = queryset.filter(
            article_id=(
                article
            ).id
        ).first()

        FavoriteAnArticleSerializer(favorited_article)

        if favorited_article:
            self.perform_destroy(favorited_article)
            message = "This article has been unfavorited successfully"
            status_code = status.HTTP_200_OK
        
        return Response(
            {
                "message": message,
                "status": status_code,
                "data": {
                    "article": {
                        "title": str(article)
                    }
                }
            },
            status_code,
        )

class UserFavouriteArticles(RetrieveAPIView):
    permission_class = IsAuthenticated
    serializer_class = ArticleSerializer
    def retrieve(self, request):

        is_authenticated(request)

        fav_articles = Article.objects.filter(
            favoriteanarticle__favorited_by = request.user.id
        ).all()
        serializer = self.serializer_class(fav_articles, many=True) 
        response = {
            "message": "retrieved all user favorite articles successfully",
            "data": serializer.data,
            "status":status.HTTP_200_OK
            }
        return Response(response, status=status.HTTP_200_OK)

class LikeUnlikeAnArticle(CreateAPIView, DestroyAPIView):
    """A user can react to an article by liking it """

    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = LikeAnArticle.objects.all()
    serializer_class = LikeAnArticleSerializer
    article_serializer_class = ArticleSerializer

    def check_article_exists(self, **kwargs):
        """
        Check whether the article with specified slug exists
        """
        try:
            article = get_object_or_404(Article, slug=kwargs.get("slug"))
            return article
        except:
            raise exceptions.ValidationError({"message": "Article doesn't exit"})

    
    def post(self, request, **kwargs):
        """
        Like an article with specified slug
        """
        message =  "You already liked this article"
        article = self.check_article_exists(**kwargs)
        like = LikeAnArticle.objects.filter(
            liked_by=request.user, article=article
        )
        if not like:
            serializer = self.serializer_class(data={"is_liked": True})
            serializer.is_valid(raise_exception=True)
            serializer.save(article=article, liked_by=request.user)

            message = "You have liked this article successfully"
        return Response(
            {
                "message": message,
                "status": status.HTTP_200_OK,
                "data": {
                    "article": {
                        "title": str(article)
                    }
                }
            },
            status=status.HTTP_200_OK,
        )

    def delete(self, request, **kwargs):
        """
        Unlike an article
        """
        queryset = LikeAnArticle.objects.filter(liked_by=request.user)
        article = self.check_article_exists(**kwargs)
        message = "You have not liked this article yet"
        status_code = status.HTTP_400_BAD_REQUEST
        liked_article = queryset.filter(
            article_id=(
                article
            ).id
        ).first()

        LikeAnArticleSerializer(liked_article)

        if liked_article:
            self.perform_destroy(liked_article)
            message = "This article has been unliked successfully"
            status_code = status.HTTP_200_OK
        
        return Response(
            {
                "message": message,
                "status": status_code,
                "data": {
                    "article": {
                        "title": str(article)
                    }
                }
            },
            status_code,
        )

class UserLikedArticles(RetrieveAPIView):
    permission_class = IsAuthenticated
    serializer_class = ArticleSerializer
    def retrieve(self, request):

        is_authenticated(request)

        liked_articles = Article.objects.filter(
            likeanarticle__liked_by = request.user.id
        ).all()
        serializer = self.serializer_class(liked_articles, many=True) 
        response = {
            "message": "retrieved all user liked articles successfully",
            "data": serializer.data,
            "status":status.HTTP_200_OK
            }
        return Response(response, status=status.HTTP_200_OK)