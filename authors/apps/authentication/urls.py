from django.urls import path
from django.contrib.auth.views import PasswordResetView,PasswordResetDoneView

from .views import (
    LoginAPIView, RegistrationAPIView, UserRetrieveUpdateAPIView, AccountActivation,
    PasswordResetView, CreateNewPasswordView)

urlpatterns = [
    path('user/', UserRetrieveUpdateAPIView.as_view()),
    path('users/', RegistrationAPIView.as_view(),name="register"),
    path('users/login/', LoginAPIView.as_view(), name="login"),
    path('users/account_verification/<token>/', AccountActivation.as_view(), name='acc_verification'),
    path('users/password-reset/', PasswordResetView.as_view(), name="reset_password"),
    path('users/change-password/<token>/', CreateNewPasswordView.as_view(), name="change_password"),
]
