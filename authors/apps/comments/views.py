from django.shortcuts import render
from rest_framework import status, exceptions
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from authors.apps.articles.models import Article, FavoriteAnArticle
from .models import Comment

from .serializers import CommentSerializer, RecursiveField
from authors.apps.articles.serializers import FavoriteAnArticleSerializer
from .renderers import CommentJSONRenderer

from django.core.serializers.json import DjangoJSONEncoder
import json
from drf_yasg.utils import swagger_auto_schema
from authors.apps.authentication.models import User
from authors.apps.authentication.serializers import UserSerializer
from django.core.mail import send_mail
import os


class CommentAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (CommentJSONRenderer,)
    serializer_class = CommentSerializer
    user_serializer_class = UserSerializer
    favorite_an_article_serializer = FavoriteAnArticleSerializer

    @swagger_auto_schema(
        operation_description='Create a Comment.',
        operation_id='Comment on an article',
        request_body=serializer_class,
        responses={201: serializer_class(many=False), 400: 'BAD REQUEST'},
    )
    def post(self, request, *args, **kwargs):
        if self.validate_comment_data(request.data):
            return self.validate_comment_data(request.data)
        comment = request.data.get('comment', {})
        slug = kwargs.get('slug')
        parent = request.data.get('comment', None).get('parent_id', None)
        article = self.get_article(slug)
        data = {**comment, "parent": parent}
        context = {"author": request.user, "article": article}
        user_info = self.user_serializer_class(User.objects.all(), many=True)
        users_id = list(map(lambda user_info: {
            "id": user_info.get('id'),
            "email": user_info.get('email')
        }, user_info.data))
        emails = [
            user['email'] for user in users_id if FavoriteAnArticle.objects.filter(
                favorited_by=user['id'],
                article=article)]
        sender = os.getenv('EMAIL_HOST_USER')
        subject = 'Author\'s Haven Notification'
        body = f"{request.user.username.title()} has commented on article titled {article}. \n{comment['body']} "
        serializer = self.serializer_class(data=data, context=context)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        response = {"message": "Comment successfuly created.",
                    "comment": serializer.data
                    }
        if emails:
            send_mail(subject, body, sender, emails, fail_silently=True)
        return Response(response, status.HTTP_201_CREATED)

    def get(self, request, **kwargs):
        slug = kwargs.get('slug')
        article = self.get_article(slug)
        queryset = Comment.objects.filter(article=article)
        if not queryset:
            return Response({
                "error": "No comments on this article yet"
            }, status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data, status.HTTP_200_OK)

    def get_article(self, slug):
        try:
            article = get_object_or_404(Article, slug=slug)
        except BaseException:
            raise exceptions.ValidationError("Article not found")
        return article

    def validate_comment_data(self, data):
        if "comment" not in data:
            return Response({
                "error": "There is no comment in the request data"
            }, status.HTTP_404_NOT_FOUND)

        if "body" not in data.get('comment'):
            return Response({
                "error": "The comment body must be provided"
            }, status.HTTP_404_NOT_FOUND)
        return False


class ManageCommentAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (CommentJSONRenderer,)
    serializer_class = CommentSerializer

    @swagger_auto_schema(
        operation_description='Edit Comment.',
        operation_id='Edit a comment on an article',
        request_body=serializer_class,
        responses={201: serializer_class(many=False), 400: 'BAD REQUEST'},
    )
    def patch(self, request, *args, **kwargs):
        slug = kwargs.get('slug')
        comment_id = kwargs.get('pk')
        article = self.get_article(slug)
        try:
            comment = Comment.objects.filter(
                article=article, id=comment_id).first()
            if not comment:
                return Response({
                    "error": "Comment not found"
                }, status.HTTP_404_NOT_FOUND)
        except BaseException:
            return Response({
                "error": "Comment id must be an integer"
            }, status.HTTP_404_NOT_FOUND)
        current_user = request.user
        comment = Comment.objects.filter(
            article=article,
            id=comment_id,
            author=current_user).first()
        if not comment:
            return Response({
                "error": "You can't edit someone else's comment"
            }, status.HTTP_401_UNAUTHORIZED)
        if self.validate_comment_data(request.data):
            return self.validate_comment_data(request.data)
        data = request.data.get('comment', {})
        context = {"author": request.user, "article": article}
        serializer = self.serializer_class(
            comment, data=data, context=context, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        response = {
            "message": "Comment successfully updated",
            "comment": serializer.data
        }
        return Response(response, status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        slug = kwargs.get('slug')
        comment_id = kwargs.get('pk')
        article = self.get_article(slug)
        try:
            comment = Comment.objects.filter(
                article=article, id=comment_id).first()
            if not comment:
                return Response({
                    "error": "Comment not found"
                }, status.HTTP_404_NOT_FOUND)
        except BaseException:
            return Response({
                "error": "Comment id must be an integer"
            }, status.HTTP_404_NOT_FOUND)
        current_user = request.user
        comment = Comment.objects.filter(
            article=article,
            id=comment_id,
            author=current_user).first()
        if not comment:
            return Response({
                "error": "Users can only delete their own comments"
            }, status.HTTP_401_UNAUTHORIZED)
        serializer = self.serializer_class(comment, partial=True)
        comment.delete()
        response = {
            "message": "Comment successfully deleted",
            "comment": serializer.data
        }
        return Response(response, status.HTTP_201_CREATED)

    def get(self, request, **kwargs):
        slug = kwargs.get('slug')
        comment_id = kwargs.get('pk')
        article = self.get_article(slug)
        try:
            queryset = Comment.objects.filter(article=article, id=comment_id)
            if not queryset:
                return Response({
                    "error": "Comment not found"
                }, status.HTTP_404_NOT_FOUND)
        except BaseException:
            return Response({
                "error": "Comment id must be an integer"
            }, status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data, status.HTTP_200_OK)

    def get_article(self, slug):
        try:
            article = get_object_or_404(Article, slug=slug)
        except BaseException:
            raise exceptions.ValidationError("Article not found")
        return article

    def validate_comment_data(self, data):
        if "comment" not in data:
            return Response({
                "error": "There is no comment in the request data"
            }, status.HTTP_404_NOT_FOUND)

        if "body" not in data.get('comment'):
            return Response({
                "error": "The comment body must be provided"
            }, status.HTTP_404_NOT_FOUND)
        return False
