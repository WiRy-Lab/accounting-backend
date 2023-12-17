"""
Test for models
"""
from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


def create_user(account='testaccount', password='testpass123'):
    """Helper function to create a user"""
    return get_user_model().objects.create_user(account, password)


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
            get_user_model().objects.create_user('', 'test123',)

    def test_create_superuser(self):
        """Test creating a new superuser"""
        user = get_user_model().objects.create_superuser(
            'testaccount',
            'test123',
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_accounting(self):
        """Test creating a new accounting is successful"""
        user = get_user_model().objects.create_user(
            account='testaccount',
            password='test123',
        )
        accounting = models.Accounting.objects.create(
            user=user,
            date='2020-01-01',
            type='income',
            amount=1000,
        )

        self.assertEqual(accounting.user, user)

    def test_create_category(self):
        """Test creating a new category is successful"""
        user = create_user()
        category = models.Category.objects.create(
            user=user,
            name='category1',
        )

        self.assertEqual(category.user, user)
        self.assertEqual(str(category), category.name)