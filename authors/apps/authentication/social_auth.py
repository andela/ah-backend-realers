# using the secrets libraries are for generating random 
# strings for times when a site has users with same name
import secrets
import string
from django.core.exceptions import ValidationError
from authors.apps.authentication.models import User


class ValidateSocialUser:
    """
    A utility class that has a method to check
    whether a user exists in the system or not
    """
    # create a random str to append to a username
    # incase users from a site have the same name
    app_random_char = ''.join(
                        secrets.choice(
                            string.ascii_letters) for i in range(7))
    def validate_system_user(self, defined_user):
        try:
            valid_user = User.objects.get(email=defined_user.get("email"))
            return {
                "email": valid_user.email,
                "token": valid_user.token
            }
        except User.DoesNotExist:

            create_new_user = {
                'email': defined_user.get('email'),
                'username': defined_user.get(
                    'name' + self.app_random_char,
                    "notknown" + self.app_random_char),
                'password': User.objects.make_random_password()}

            new_app_user = User.objects.create_user(**create_new_user)
            new_app_user.is_active = True
            new_app_user.save()

            return {
                'email': defined_user.get('email'),
                'token': new_app_user.token
            }
