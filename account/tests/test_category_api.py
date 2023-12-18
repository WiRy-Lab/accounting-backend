"""
Test for category api
"""
from datetime import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Category, Accounting

from account.serializers import CategorySerializer


CATEGORY_URL = reverse('accounting:category-list')


def detail_url(category_id):
    """Return category detail URL"""
    return reverse('accounting:category-detail', args=[category_id])


def create_user(account='testaccount', password='testpass123'):
    """Helper function to create a user"""
    return get_user_model().objects.create_user(account, password)


class PublicCategoryApiTests(TestCase):
    """Test unauthenticated category API requests"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that auth is required for retrieving category"""
        res = self.client.get(CATEGORY_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateCategoryApiTests(TestCase):
    """Test the authorized user category API"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)

    def test_retrieve_category(self):
        """Test retrieving a list of category"""
        Category.objects.create(user=self.user, name='Food')
        Category.objects.create(user=self.user, name='Transportation')

        res = self.client.get(CATEGORY_URL)

        category = Category.objects.all().order_by('-name')
        serializer = CategorySerializer(category, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_category_limit_to_user(self):
        """Test that category returned are for authenticated user"""
        user2 = create_user(account='testaccount2', password='testpass123')
        Category.objects.create(user=user2, name='Food')
        category = Category.objects.create(user=self.user, name='Transportation')

        res = self.client.get(CATEGORY_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], category.name)
        self.assertEqual(res.data[0]['id'], category.id)


    def test_update_category(self):
        """Test updating a category with patch"""
        category = Category.objects.create(user=self.user, name='Food')
        payload = {'name': 'Transportation'}
        url = detail_url(category.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        category.refresh_from_db()
        self.assertEqual(category.name, payload['name'])

    def test_delete_category(self):
        """Test deleting a category"""
        category = Category.objects.create(user=self.user, name='Food')
        url = detail_url(category.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        categories = Category.objects.filter(user=self.user)
        self.assertFalse(categories.exists())

    def test_create_category(self):
        """Test creating a new category"""
        payload = {'name': 'Food'}
        self.client.post(CATEGORY_URL, payload)

        exists = Category.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()
        self.assertTrue(exists)

    def test_filter_categories_assigned_to_accounting(self):
        """Test filtering categories by those assigned to accounting"""
        category1 = Category.objects.create(user=self.user, name='Food')
        category2 = Category.objects.create(user=self.user, name='Transportation')
        accounting = Accounting.objects.create(
            date=datetime.now().strftime('%Y-%m-%d'),
            user=self.user,
            type='outcome',
            amount=50,
        )
        accounting.category.add(category1)

        res = self.client.get(CATEGORY_URL, {'assigned_only': 1})

        serializer1 = CategorySerializer(category1)
        serializer2 = CategorySerializer(category2)
        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_retrieve_categories_assigned_unique(self):
        """Test filtering categories by assigned returns unique items"""
        category = Category.objects.create(user=self.user, name='Food')
        Category.objects.create(user=self.user, name='Transportation')
        accounting1 = Accounting.objects.create(
            date=datetime.now().strftime('%Y-%m-%d'),
            user=self.user,
            type='outcome',
            amount=50,
        )
        accounting1.category.add(category)
        accounting2 = Accounting.objects.create(
            date=datetime.now().strftime('%Y-%m-%d'),
            user=self.user,
            type='outcome',
            amount=50,
        )
        accounting2.category.add(category)

        res = self.client.get(CATEGORY_URL, {'assigned_only': 1})

        self.assertEqual(len(res.data), 1)