"""
Tests for user api
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('auth:register')
TOKEN_URL = reverse('auth:login')
ME_URL = reverse('auth:me')


def create_user(**params):
    """Helper function to create new user"""
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """Test the public features of the user API"""

    def setUp(self):
        """Create client"""
        self.client = APIClient()

    def test_create_user_success(self):
        """Test creating user with valid payload is successful"""
        payload = {
            'account': 'apiccount',
            'password': 'testpass123',
            'password_verify': 'testpass123',
            'email': 'apitest@example.com',
            'name': 'ApiTest',
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(account=payload['account'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_with_email_exists(self):
        """Test creating user that already exists fails"""
        payload = {
            'account': 'apiccount',
            'password': 'testpass123',
            'email': 'apitest@example.com',
            'name': 'ApiTest',
        }
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_password_mismatch(self):
        """Test creating a user with mismatched passwords fails"""
        payload = {
            'account': 'apiccount',
            'password': 'testpass123',
            'password_verify': 'testpass321',
            'email': 'apitest@example.com',
            'name': 'ApiTest',
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Passwords must match', str(res.data['non_field_errors']))
        user_exists = get_user_model().objects.filter(email=payload['account']).exists()
        self.assertFalse(user_exists)

    def test_pass_word_too_short(self):
        """Test that password must be more than 5 characters"""
        payload = {
            'account': 'apiccount',
            'password': 'pw',
            'password_verify': 'pw',
            'email': 'apitest@example.com',
            'name': 'ApiTest',
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            account=payload['account']
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Test generating token for valid credentials"""
        user_details = {
            'account': 'apiccount',
            'password': 'testpass123',
            'email': 'apitest@example.com',
            'name': 'ApiTest',
        }
        create_user(**user_details)

        payload = {
            'account': user_details['account'],
            'password': user_details['password'],
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_bad_credentials(self):
        """Test that token is not created with invalid credentials"""
        create_user(account='apiccount', password='goodpass', email='apitest@example.com')
        payload = {
            'account': 'apiccount',
            'password': 'badpass',
            'email': 'apitest@example.com',
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_blank_password(self):
        """Test posting blank password returns error"""
        payload = {
            'account': 'apiccount',
            'password': '',
            'email': 'apitest@example.com',
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        """Test that authentication is required for users"""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """Test api requests that require authentication"""

    def setUp(self):
        """Create client and user"""
        self.user = create_user(
            account='apiccount',
            password='testpass123',
            email='apitest@example.com',
            name='ApiTest',
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_user_profile_success(self):
        """Test retrieving profile for logged in user"""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'account': self.user.account,
            'email': self.user.email,
            'name': self.user.name,
        })

    def test_post_me_not_allowed(self):
        """Test that post is not allowed for me endpoint"""
        res = self.client.post(ME_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """Test updating user profile for authenticated user"""
        payload = {
            'password': 'newpass123',
            'name': 'NewName',
        }
        res = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_login_creates_new_token(self):
        """Test that logging in creates a new token"""
        user_details = {
            'account': 'testaccount1',
            'password': 'testpass123',
            'email': 'apitest@example.com',
            'name': 'ApiTest',
        }
        create_user(**user_details)

        payload = {
            'account': user_details['account'],
            'password': user_details['password'],
        }
        res = self.client.post(TOKEN_URL, payload)
        first_token = res.data['token']

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('token', res.data)

        res = self.client.post(TOKEN_URL, payload)
        second_token = res.data['token']

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('token', res.data)
        self.assertNotEqual(first_token, second_token)
