from rest_framework import status
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist

from .models import Profile
from .renderers import ProfileJSONRenderer
from .serializers import ProfileSerializer
from .exceptions import ProfileDoesNotExist
from drf_yasg.utils import swagger_auto_schema

class UpdateGetUserProfileAPIView(RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (ProfileJSONRenderer,)
    serializer_class = ProfileSerializer
    allowed_methods = ('GET','PATCH')
    @swagger_auto_schema(
        operation_id='Retrieve User Profile',
        request_body=serializer_class,
        responses={201: serializer_class(many=False), 400: 'BAD REQUEST'},
    )
    def retrieve(self, request, username, *args, **kwargs):
        # Try to retrieve the requested profile and throw an exception if the
        # profile could not be found.
        try:
            # We use the `select_related` method to avoid making unnecessary
            # database calls.
            profile = Profile.objects.select_related('user').get(
                user__username=username
            )
        except Profile.DoesNotExist:
            raise ProfileDoesNotExist

        serializer = self.serializer_class(profile)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_id='Update User\'s Profile',
        request_body=serializer_class,
        responses={201: serializer_class(many=False), 400: 'BAD REQUEST'},
    )
    def patch(self, request, *args, **kwargs):
        username = self.kwargs.get("username")
        try:
            get_user_model().objects.get(
                username=username
            )
        except ObjectDoesNotExist:
            return Response(
                {"detail": "No user found with the provided username {}".format(username)},
                status=status.HTTP_404_NOT_FOUND,
            )
            
        profile = Profile.objects.get(user=kwargs.get('username'))

        if not profile.user.pk == request.user.id:
            return Response(
                {"detail": "You don't have permissions to update this user"},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = self.serializer_class(
            profile, data=request.data.get('profile',{}), partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)
