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

from .renderers import UserJSONRenderer
from .serializers import (
    LoginSerializer, RegistrationSerializer, UserSerializer,
    ResetPasswordSerializer, SetNewPasswordSerializer
)

from drf_yasg.utils import swagger_auto_schema

from .backends import (
    AccountVerification
)


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
        try:
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
        except KeyError:
            raise exceptions.ValidationError("Please provide a valid Email Address")

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
