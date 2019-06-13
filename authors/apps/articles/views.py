from django.shortcuts import render
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from .serializers import ArticleSerializer
from .models import Article
from authors.apps.authentication.models import User
from rest_framework.response import Response


class ArticleView(ListCreateAPIView):
    serializer_class = ArticleSerializer
    permission_classes = (IsAuthenticated,)
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
    permission_classes = (IsAuthenticated, )
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
        
        return Response(serializer.data, status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        article = Article.objects.filter(slug=kwargs.get('slug')).first()
        if not article:
            return Response({
                 "message": "Article does not exist"
            }, status.HTTP_404_NOT_FOUND)
        if request.user.username != article.author.username:
            return Response({
                 "message": "You do not have permision to update this article"
            }, status.HTTP_401_UNAUTHORIZED)

        serializer = self.serializer_class(
            article, 
            data=request.data.get("article", {}), 
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        response = {"success": "Article successfully updated!", "data": serializer.data}
        return Response(response, status.HTTP_200_OK)

    def delete(self, request, **kwargs):
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

