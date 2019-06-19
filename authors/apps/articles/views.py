from django.shortcuts import render
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView,RetrieveAPIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from .serializers import ArticleSerializer
from .models import Article
from authors.apps.authentication.models import User
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
class ArticleView(ListCreateAPIView):
    serializer_class = ArticleSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = Article.objects.all()


    def post(self, request):
        article = request.data.get("article", {})

        serializer = self.serializer_class(data=article)
        serializer.is_valid(raise_exception=True)
        serializer.save(
            author=User.objects.filter(username=request.user.username).first()
        )
        response = {"success": "Article successfully created!", "data": serializer.data}
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
                 "message": "Article does not exist"
            }, status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(
            article, 
            partial=True
        )

        return Response({
            "data": serializer.data,
        }, status.HTTP_200_OK)

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

        article_data =  request.data.get("article", {})
        if article_data:
            serializer = self.serializer_class(
                article, 
                data=article_data, 
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            response = {"success": "Article successfully updated!", "data": serializer.data}
            return Response(response, status.HTTP_200_OK)
        return Response({
                 "message": "Please use proper request body!",
                 "status":status.HTTP_400_BAD_REQUEST
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
        response = {"success": "Article successfully deleted!", "article": serializer.data}
        return Response(response, status.HTTP_200_OK)

def is_authenticated(request):
    user = request.user.id
    
    if user == None:
        raise PermissionDenied({
            "message":"Please Login to proceed",
            "status":status.HTTP_403_FORBIDDEN
        })
