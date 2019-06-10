from django.urls import path

from .views import UpdateGetUserProfileAPIView

app_name = 'profiles'
urlpatterns = [
    path('<str:username>/', UpdateGetUserProfileAPIView.as_view(),name="view_profile"),
]
