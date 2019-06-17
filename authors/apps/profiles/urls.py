from django.urls import path

from .views import UpdateGetUserProfileAPIView, FollowProfileAPIView, FollowersAndFollowingAPIView

app_name = 'profiles'
urlpatterns = [
    path('<str:username>/follow/', FollowProfileAPIView.as_view(),name="follow"),
    path('follow_status/', FollowersAndFollowingAPIView.as_view(),name="following"),
    path('<str:username>/', UpdateGetUserProfileAPIView.as_view(),name="view_profile"),
]
