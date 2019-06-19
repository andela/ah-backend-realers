from rest_framework import status, exceptions
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings
from .models import User

from itsdangerous import URLSafeTimedSerializer, exc
from django.core.mail import send_mail

import os, re
from rest_framework import exceptions

from .renderers import UserJSONRenderer
from .serializers import (
    LoginSerializer, RegistrationSerializer, UserSerializer,
    ResetPasswordSerializer, SetNewPasswordSerializer,
    FacebookAndGoogleSerializer, TwitterSerializer
)

import facebook
import twitter
from google.auth.transport import requests
from google.oauth2 import id_token
from drf_yasg.utils import swagger_auto_schema

from .backends import (
    AccountVerification
)
from authors.apps.profiles.models import Profile
from .social_auth import ValidateSocialUser


check_user = ValidateSocialUser()

class RegistrationAPIView(APIView):
    # Allow any user (authenticated or not) to hit this endpoint.
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = RegistrationSerializer

    @swagger_auto_schema(
        operation_description='Regester a new User.',
        operation_id='Sign up as a new user',
        request_body=serializer_class,
        responses={201: serializer_class(many=False), 400: 'BAD REQUEST'},
    )
    def post(self, request):
        user = request.data.get('user', {})
        # The create serializer, validate serializer, save serializer pattern
        # below is common and you will see it a lot throughout this course and
        # your own work later on. Get familiar with it.
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        AccountVerification().send_verification_email(user.get('email'), request)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class LoginAPIView(APIView):
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = LoginSerializer

    @swagger_auto_schema(
        operation_description='Login User.',
        operation_id='login as a user',
        request_body=serializer_class,
        responses={201: serializer_class(many=False), 400: 'BAD REQUEST'},
    )
    def post(self, request):
        user = request.data.get('user', {})

        # Notice here that we do not call `serializer.save()` like we did for
        # the registration endpoint. This is because we don't actually have
        # anything to save. Instead, the `validate` method on our serializer
        # handles everything we need.
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class UserRetrieveUpdateAPIView(RetrieveUpdateAPIView):

    """
    retrieve: Get User Details
    Update: Update User Details
    """

    permission_classes = (IsAuthenticated,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = UserSerializer

    @swagger_auto_schema(
        operation_id='Retrieve User Details',
        request_body=serializer_class,
        responses={201: serializer_class(many=False), 400: 'BAD REQUEST'},
    )
    def retrieve(self, request, *args, **kwargs):
        # There is nothing to validate or save here. Instead, we just want the
        # serializer to handle turning our `User` object into something that
        # can be JSONified and sent to the client.
        serializer = self.serializer_class(request.user)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_id='Update User Details',
        request_body=serializer_class,
        responses={201: serializer_class(many=False), 400: 'BAD REQUEST'},
    )

    def update(self, request, *args, **kwargs):
        serializer_data = request.data.get('user', {})

        serializer = self.serializer_class(
            request.user, data=serializer_data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

class AccountActivation(APIView):
    def get(self, request, **kwargs):
        activation_key = kwargs.get('token')
        user = AccountVerification().verify_token(activation_key)
        response = AccountVerification.verify_user(user)
        return Response(response)


class PasswordResetView(APIView):
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = ResetPasswordSerializer

    @classmethod
    def check_email(cls, email):
        not_email = not email
        invalid_email = not re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", email)
        
        if not_email or invalid_email:
            msg = "The email field can not be blank"
        
            raise exceptions.ValidationError(msg) if not_email else \
                exceptions.ValidationError("Provide a valid email address")
        return None

    def email_verification(self, email):
        user = User.objects.filter(email = email).first() \
            if not PasswordResetView.check_email(email) else None
        if not user:
            raise exceptions.ValidationError("This Email Address is not attached to any account")

    @swagger_auto_schema(
        operation_description='Reset Password.',
        operation_id='reset password via email',
        request_body=serializer_class,
        responses={200: serializer_class(many=False), 400: 'BAD REQUEST'},
    )
    def post(self, request):
        if 'email' not in request.data:
            raise exceptions.ValidationError("Please provide an Email Address")
        email=request.data["email"]
        
        self.email_verification(email)

        serializer = URLSafeTimedSerializer(os.environ.get("SECRET_KEY"))
        token = serializer.dumps(email, salt=os.environ.get("SECURITY_PASSWORD_SALT"))
        
        BASE_URL = request.get_host()
        url_scheme = request.scheme
        reset_link = "{}://{}/api/users/change-password/{}/".format(url_scheme,BASE_URL,token)
        recipient = [email]
        sender = os.getenv('EMAIL_HOST_USER')
        subject = 'Author\'s Haven Password Reset'
        body = "You requested to change your account password.\n\
Click on the link below to complete changing your password.\n\n{}\n\
Ignore and Delete this email if you did not make this request.\n\n\t\
Author\'s Haven by The Realers.".format(reset_link)
        
        send_mail(subject, body, sender, recipient, fail_silently=True)

        data = {
            "message": "Please check your email inbox for the Password Reset link we've sent",
            "status": status.HTTP_200_OK
        }
        return Response(data, status=status.HTTP_200_OK)
        


class CreateNewPasswordView(APIView):
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = SetNewPasswordSerializer
    def password_verification(self, password, confirm_password):
        if (not password) or (not confirm_password):
            raise exceptions.ValidationError("Provide both Password and Confirm_Password fields")
        if len(password) < 8:
            raise exceptions.ValidationError("Password length must be 8 or more characters")
        if password != confirm_password:
            raise exceptions.ValidationError("Password is not macthing with Confirm_password!")

    @swagger_auto_schema(
        operation_description='Set new Password.',
        operation_id='Set new password using link sent in email',
        request_body=serializer_class,
        responses={201: serializer_class(many=False), 400: 'BAD REQUEST'},
    )
    def patch(self, request, token):
        try:
            new_password = request.data.get("password")
            confirm_new_password = request.data.get("confirm_password")

            self.password_verification(new_password,confirm_new_password)
            
            serializer = URLSafeTimedSerializer(os.environ.get("SECRET_KEY"))
            email = serializer.loads(token, salt=os.environ.get("SECURITY_PASSWORD_SALT"),
                max_age=3600*12*365)
            
            user = User.objects.filter(email = email).first()
            user.set_password(new_password)
            user.save()
            return Response({
                "message": "You have succesfully reset your password",
                "status": status.HTTP_201_CREATED
            })
        except exc.BadSignature:
            raise exceptions.ValidationError("This is an invalidated link")


class FacebookAPIView(APIView):
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = FacebookAndGoogleSerializer

    @swagger_auto_schema(
        operation_description='Social Auth with Facebook',
        operation_id='Login in a user using their Facebook credentials',
        request_body=serializer_class,
        responses={200: serializer_class(many=False), 400: 'BAD REQUEST'},
    )
    def post(self, request):

        user_data = request.GET.get("access_token")
        # get the token
        try:
            facebook_acct_user = facebook.GraphAPI(access_token=user_data)
            user_details = facebook_acct_user.get_object(
                id='me', fields='id, name, email')

            facebook_user = check_user.validate_system_user(user_details)

            return Response(facebook_user, status=status.HTTP_200_OK)
            
        except:
            return Response(
                {"error": "Facebook login failed. Token is expired or invalid"}, status=status.HTTP_400_BAD_REQUEST)


class GoogleAPIView(APIView):
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = FacebookAndGoogleSerializer

    @swagger_auto_schema(
        operation_description='Social Auth with Google',
        operation_id='Login in a user using their google credentials',
        request_body=serializer_class,
        responses={200: serializer_class(many=False), 400: 'BAD REQUEST'},
    )
    def post(self, request):

        googl_auth_token = request.GET.get("access_token")
        # get the token
        try:
            user_cred = id_token.verify_oauth2_token(
                googl_auth_token, requests.Request())

            verified_user = check_user.validate_system_user(user_cred)

            return Response(verified_user, status=status.HTTP_200_OK)
            
        except:
            return Response(
                {"error": "google login failed. Token is either invalid or expired"}, status=status.HTTP_400_BAD_REQUEST)


class TwitterAPIView(APIView): 
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = TwitterSerializer

    @swagger_auto_schema(
        operation_description='Social Auth with Twitter',
        operation_id='Authenticate user using Twitter',
        request_body=serializer_class,
        responses={200: serializer_class(many=False), 400: 'BAD REQUEST'},
    )
    def post(self, request): # pragma: no cover

        twitter_token = request.GET.get("access_token")
        twitter_token_secret = request.GET.get("access_token_secret")
        # get the token and related twitter stuff
        
        try:
            from_twitter_api = twitter.Api(
                consumer_key=os.getenv("TWITTER_CONSUMER_KEY", ""),
                consumer_secret=os.getenv("TWITTER_CONSUMER_SECRET", ""),
                access_token_key=twitter_token,
                access_token_secret=twitter_token_secret
            )
            user_details = from_twitter_api.VerifyCredentials(include_email=True)
            
            # get user details as a dictionary/ json format
            user_details = user_details.__dict__
            twitter_user_exist = check_user.validate_system_user(user_details)
            return Response(twitter_user_exist, status=status.HTTP_200_OK)
            
        except:
            return Response(
                {"error": "Twitter login failed. Token either expired or invalid"}, status=status.HTTP_400_BAD_REQUEST)
        
        