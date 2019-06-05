from .test_base import TestBase
import json
from rest_framework import status


class BackEndTestCases(TestBase):

    def test_confirmation_token_is_generated(self):
        """
        Test to verify that the verification token is generated when an 
        email addresss is provided to it.
        """
        token = self.acc_verify().generate_confirmation_token(
            self.user_data['user']['email'])

        self.assertGreaterEqual(len(token), 50)

    def test_token_verification_returns_email(self):
        """
        Test to verify that the verification token is generated when an 
        email addresss is provided to it.
        """
        email = self.acc_verify().verify_token(self.known_key)

        self.assertEqual(self.user_data_2['user']['email'], email)

    def test_token_verification_with_invalid_token(self):
        """
        Test to verify that the verify_token() 
        returns false when invalid token is provided.
        """
        key_invalid = self.acc_verify().verify_token(self.invalid_key)

        self.assertEqual(False, key_invalid)

    def test_account_activation_of_new_signup(self):
        """
        Test to verify that a new signup is
        successfully activated
        """
        response = self.acc_verify.verify_user(self.user_data_2['user']['email'])
        expected = "User with email {} has been activated".format(
            self.user_data_2['user']['email'])
        self.assertEqual(expected, response)

    def test_account_activation_of_existent_user(self):
        """
        Test to verify that a existent user are skipped from being activated
        """
        self.acc_verify.verify_user(self.user_data['user']['email'])
        response = self.acc_verify.verify_user(self.user_data['user']['email'])
        expected = "Account with {} is already active".format(
            self.user_data['user']['email'])
        self.assertEqual(expected, response)
