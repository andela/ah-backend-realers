from rest_framework import status
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .renderers import UserJSONRenderer
from .serializers import (
    LoginSerializer, RegistrationSerializer, UserSerializer
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
