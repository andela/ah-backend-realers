from django.urls import path

from .views import (
    LoginAPIView, RegistrationAPIView, UserRetrieveUpdateAPIView, AccountActivation
)

urlpatterns = [
    path('user/', UserRetrieveUpdateAPIView.as_view()),
    path('users/', RegistrationAPIView.as_view(),name="register"),
    path('users/login/', LoginAPIView.as_view(), name="login"),
    path('users/account_verification/<token>/', AccountActivation.as_view(), name='acc_verification'),
]
