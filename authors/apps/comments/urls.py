from django.urls import path
from .views import CommentAPIView, ManageCommentAPIView

app_name = 'comments'
urlpatterns = [
    path('<slug:slug>/comments/', CommentAPIView.as_view(), name="create_comment"),
    path('<slug:slug>/comments/', CommentAPIView.as_view(), name="get_comments"),
    path('<slug:slug>/comments/<pk>', ManageCommentAPIView.as_view(), name="edit_comment"),
    path('<slug:slug>/comments/<pk>', ManageCommentAPIView.as_view(), name="delete_comment"),
    path('<slug:slug>/comments/<pk>', ManageCommentAPIView.as_view(), name="get_comment"),
]