from django.shortcuts import render
from rest_framework.generics import (
    ListCreateAPIView, RetrieveUpdateDestroyAPIView, CreateAPIView, DestroyAPIView, RetrieveAPIView)
from rest_framework import status,exceptions
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from .serializers import ArticleSerializer, FavoriteAnArticleSerializer
from .models import Article, FavoriteAnArticle
from authors.apps.authentication.models import User
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from django.shortcuts import get_object_or_404,get_list_or_404
import json 
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import PermissionDenied
from .pagination import ArticleSetPagination

from authors.apps.article_tagging.views import ArticleTaggingViewSet

class ArticleView(ListCreateAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = ArticleSetPagination

    def post(self, request):
        article = request.data.get("article", {})
        check_tag_is_provided(article)
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
        article_object = Article.objects.filter(slug=kwargs.get('slug')).first()
        if not article_object:
            return Response({
                "message": "Article does not exist"
            }, status.HTTP_404_NOT_FOUND)
        if request.user.username != article_object.author.username:
            return Response({
                "message": "You do not have permision to update this article"
            }, status.HTTP_401_UNAUTHORIZED)

        article = request.data.get("article", {})
        if article:
            check_tag_is_provided(article)
            serializer = self.serializer_class(
                article_object,
                data=article,
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
        response = {"success": "Article successfully deleted!",
                    "article": serializer.data}
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

def check_tag_is_provided(article):
    if "tagName" in article:
        #create tag if it doesnt exist
        tag_names = ArticleTaggingViewSet.create_tag_if_provided_is_inexistent(
            ArticleTaggingViewSet, article.get('tagName')
        )

        article['tagName'] = tag_names
