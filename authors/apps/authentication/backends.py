import jwt

from django.conf import settings

from rest_framework import authentication, exceptions

from .models import User

from authors.apps.authentication.auth_token import AuthenticationToken

authentication_token = AuthenticationToken()

class JWTAuthentication(authentication.BaseAuthentication):
    authentication_header_prefix = "Bearer"
    def authenticate(self, request):
        auth_headers = authentication.get_authorization_header(request).split()
        if len(auth_headers) != 2:
            return None

        token = auth_headers[1].decode("utf-8")

        return self.authenticate_credentials(request, token)

    def authenticate_credentials(self, request, token):
        user_id = authentication_token.decode_auth_token(token)
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed("Email does not exist. Please signup")
        if not user.is_active:
            raise exceptions.AuthenticationFailed("User is not active")
        return (user, token)
        