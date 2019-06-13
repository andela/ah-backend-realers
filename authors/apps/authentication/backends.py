import jwt
from .models import User
from itsdangerous import URLSafeTimedSerializer
from os import environ
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings

from rest_framework import authentication, exceptions

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
            raise exceptions.AuthenticationFailed(
                "This account does not exist. Please signup")
        if not user.is_active:
            raise exceptions.AuthenticationFailed("This account is not yet active")
        return (user, token)


class AccountVerification:

    def generate_confirmation_token(self, email):
        # generate a token using the email address obtained during user registration
        # Salted with the SECRET KEY
        serializer = URLSafeTimedSerializer(environ.get("SECRET_KEY"))
        return serializer.dumps(email, salt=environ.get("SECURITY_PASSWORD_SALT"))

    def verify_token(self, token, expiration=3600*12*365):
        # verify that the link is still active
        serializer = URLSafeTimedSerializer(environ.get("SECRET_KEY"))
        try:
            email = serializer.loads(
                token,
                salt=environ.get("SECURITY_PASSWORD_SALT"),
                max_age=expiration
            )
        except:
            return False
        return email

    @staticmethod
    def verify_user(email):
        # change the account is_active to True, if the email exists.
        is_active = User.objects.filter(
            email=email).values_list('is_active', flat=True)
        try:
            if not is_active[0]:
                user = User.objects.get(email=email)
                user.is_active = True
                user.save()
                return "User with email {} has been activated".format(email)
            return "Account with {} is already active".format(email)
        except:
            return "Account doesn't exist"

    def send_verification_email(self, email, request):

        kwargs = {
            "token": self.generate_confirmation_token(email),
        }

        verification_url = reverse( 
            "authentication:acc_verification", kwargs=kwargs)

        activation_url = "{0}://{1}{2}".format(
            request.scheme, request.get_host(), verification_url
        )

        subject = "Author's Haven - Account Activation"
        message = 'Go to this link to activate your account {}'.format(
            activation_url)
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [email, ]
        send_mail(subject, message, email_from, recipient_list)
