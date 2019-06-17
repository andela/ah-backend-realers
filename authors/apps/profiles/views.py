from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework.exceptions import ValidationError, NotFound
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist, ValidationError

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


class FollowProfileAPIView(APIView):

    permission_classes = (IsAuthenticated,)
    renderer_classes = (ProfileJSONRenderer,)
    serializer_class = ProfileSerializer

    def delete(self, request, username=None):

        profile_followa = self.request.user.profile

        try:
            profile_followed = Profile.objects.get(
                user__username=username)
        except Profile.DoesNotExist: 
            raise ProfileDoesNotExist

        if not profile_followa.is_following(profile_followed):
            raise serializers.ValidationError(
                "Can not unfollow author you do not follow")


        profile_followa.unfollow(profile_followed)

        serializer = self.serializer_class(profile_followed, context={
            'request': request
        })

        response = {
            "data":serializer.data['username'],
            "message":"You have just unfollowed this author",
            "status":status.HTTP_200_OK
        }

        return Response(response, status=status.HTTP_201_CREATED)

    def post(self, request, username=None):
        follower = self.request.user.profile

        try:
            profile_followed = Profile.objects.get(user__username=username)
        except Profile.DoesNotExist:
            raise NotFound('No profile matches this username')

        if follower.pk is profile_followed.pk:
            raise serializers.ValidationError( # pragma: no cover
                'As an author you can not follow yourself.')

        if follower.is_following(profile_followed):
            raise serializers.ValidationError(
                'You already follow this author')

        follower.follow(profile_followed)

        serializer = self.serializer_class(profile_followed, context={
            'request': request
        })

        response = {
            "data":serializer.data['username'],
            "message":"You have followed this author",
            "status":status.HTTP_201_CREATED
        }

        return Response(response, status=status.HTTP_201_CREATED)

class FollowersAndFollowingAPIView(APIView):
    """
    View will fetch returns users that follow an author and
    whom the author follows """
    serializer_class = ProfileSerializer
    renderer_classes = (ProfileJSONRenderer,)
    permission_classes = (IsAuthenticated,)
    allowed_methods = ('GET',)

    def get(self, request):
        """
        Gets the author's followers and those the author follows
        """

        profile = Profile.objects.get(
            user__username=request.user.username
        )
        
        user_follows = profile.following.all()
        user_followed_by = profile.followed_by.all()

        follower_serializer = self.serializer_class(
        user_follows, many=True, context={
            'request': request
        })

        following_serializer = self.serializer_class(
        user_followed_by, many=True, context={
            'request': request
        })

        followed_by_author = [user.get("username") for user in follower_serializer.data]
        following_author = [author.get("username") for author in following_serializer.data]


        response = {
            "Author_Followers":{
            "Total": len(following_serializer.data),
            "authors_by_username": following_author
        },
        "Author_Follows":{
            "total": len(follower_serializer.data),
            "authors_by_username": followed_by_author
        }
        }
        return Response(response, status=status.HTTP_200_OK)
