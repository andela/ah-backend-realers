
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from authors.apps.authentication.models import User

class AuthorFollowAPIViewTestCase(APITestCase):

    def setUp(self):        
        test_followa = User.objects.create_user(
            email="nakooye@tests.com", 
            password="donthack",
            username="kaffulu")

        testy_followy = User.objects.create_user(
            email="greatest@coder.com", 
            password="donthack",
            username="zipliner")
        testy_followy.is_active = True
        testy_followy.save()

        self.client = APIClient()
        self.client.force_authenticate(user=test_followa)


    def test_non_authenticated_user_cannot_follow_author(self):
        # log out client
        self.client.logout()
        response = self.client.post(
            '/api/profiles/zipliner/follow/'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_non_authenticated_user_check_following_stats(self):
        # log out the client before the test
        self.client.logout()
        response = self.client.get(
            '/api/profiles/follow_status/'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_authentic_author_unable_to_follow_nonexistent_user(self):
        response = self.client.post(
            '/api/profiles/jajawo/follow/'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_authentic_author_follow_other_author(self):
        response = self.client.post(
            '/api/profiles/zipliner/follow/'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_authentic_author_unable_refollow_already_followed_author(self):
        response = self.client.post(
            '/api/profiles/zipliner/follow/'
        )
        response = self.client.post(
            '/api/profiles/zipliner/follow/'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_authentic_author_can_unfollow_authors_they_follow(self):
        response = self.client.post(
            '/api/profiles/zipliner/follow/'
        )
        response = self.client.delete(
            '/api/profiles/zipliner/follow/'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_authentic_author_cannot_unfollow_users_they_are_not_following(self):
        response = self.client.delete(
            '/api/profiles/zipliner/follow/'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_authentic_author_cannot_unfollow_non_existent_profile(self):
        response = self.client.delete(
            '/api/profiles/museveni/follow/'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_authentic_authors_can_see_their_followers_and_followees(self):
        response = self.client.get(
            '/api/profiles/follow_status/'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
