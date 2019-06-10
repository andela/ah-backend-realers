from ..models import Profile
from .test_base import ProfileTestBase
from authors.apps.authentication.models import User
from rest_framework import status
class ModelProfileTestCase(ProfileTestBase):

    def test_profile_object_returns_username(self):
        
        u = User.objects.first()
        profile = u.profile
        self.assertIn('testuser', str(profile))





