"""
Test for models
"""
from django.test import TestCase
from django.contrib.auth import get_user_model

class ModelTests(TestCase):
    """Test for models"""

    def test_create_user_with_account_successful(self):
        """Test creating a new user with account is successful"""
        account = 'testaccount'
        password = 'testpass123'
        email = 'test@example.com'
        user = get_user_model().objects.create_user(
            account=account,
            password=password,
            email=email,
        )

        self.assertEqual(user.account, account)
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_without_account_raises_error(self):
        """Test that creating user without account raises error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'test123')

    def test_create_superuser(self):
        """Test creating a new superuser"""
        user = get_user_model().objects.create_superuser(
            'testaccount',
            'test123',
        )

        self.assertTrue(user.is_superuser)

