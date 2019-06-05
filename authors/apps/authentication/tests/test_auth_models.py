from .test_base import TestBase
from ..models import User, UserManager

class ModelUserTestCase(TestBase):
    """ 
    A class to test the authentication models class User
    """

    def test_create_a_model_auth_user(self):

        #check db and get how many users are there
        initial_users = User.objects.count()
        
        #add another user
        self.new_db_user.save()

        self.assertEqual(self.username, self.new_db_user.get_short_name())
        self.assertEqual(self.username, self.new_db_user.get_full_name)

        # test the user class private method __str__
        self.assertEqual(self.email, str(self.new_db_user))

        # recount users
        new_users_total = User.objects.count()

        # test number of initial users against number after new user
        self.assertNotEqual(new_users_total, initial_users)


class  ModelUserManagerTestCase(TestBase):
    """
    A test class that tests the UserManager class the 
    authentication models 
    """

    def test_create_normal_user_with_no_username(self):
       
        with self.assertRaises(TypeError):
            User.objects.create_user(
                email=self.email, 
                password=self.password,
                username=None
            )

    def test_create_normal_user_with_no_email_address(self):
       
        with self.assertRaises(TypeError):
            User.objects.create_user(
                username=self.username, 
                password=self.password,
                email=None
            )

    def test_create_app_super_user(self):

        # count users in db
        number_of_db_objects = User.objects.count()
        user = User.objects.create_superuser(
            email=self.email, 
            password=self.password,
            username=self.username)

        # check whether created user is a superuser
        self.assertTrue(user.is_superuser)

        #assert if created user is staff
        self.assertTrue(user.is_staff)

        # recount users in db
        new_number_users = User.objects.count()

        # test against the two users in db checks
        self.assertNotEqual(number_of_db_objects, new_number_users)

    def test_create_super_user_with_password_none(self):
       
        with self.assertRaises(TypeError):
            User.objects.create_superuser(
                email=self.email, 
                password=None,
                username=self.username
            )
