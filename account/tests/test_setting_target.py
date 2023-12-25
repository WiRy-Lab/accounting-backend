"""
Test settings target
"""
from django.urls import reverse
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from core.models import MonthTarget, SaveMoneyTarget, Category
from account.serializers import MonthTargetSerializer, SaveMoneyTargetSerializer

from datetime import datetime


MONTH_TARGET_URL = reverse('accounting:month_target-list')
SAVE_MONEY_TARGET_URL = reverse('accounting:save_money_target-list')


def create_user(account='testaccount', password='testpass123'):
    """Helper function to create a user"""
    return get_user_model().objects.create_user(account, password)


class PublicSettingsTargetApiTests(TestCase):
    """Test the publicly available settings target API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required for retrieving settings target"""
        res = self.client.get(MONTH_TARGET_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

        res = self.client.get(SAVE_MONEY_TARGET_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateSettingsTargetApiTests(TestCase):
    """Test the authorized user settings target API"""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_month_target(self):
        """Test retrieving a list of month target"""
        MonthTarget.objects.create(user=self.user, income=1000000, outcome=2000, month=datetime.now().month, year = datetime.now().year)
        MonthTarget.objects.create(user=self.user, income=1000000, outcome=500, month=datetime.now().month - 1 , year = datetime.now().year)

        res = self.client.get(MONTH_TARGET_URL)

        month_target = MonthTarget.objects.all().order_by('-year', '-month')
        serializer = MonthTargetSerializer(month_target, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_save_money_target(self):
        """Test retrieving a list of save money target"""
        category = Category.objects.create(user=self.user, name='test category')
        SaveMoneyTarget.objects.create(user=self.user, target=1000000, category=category)

        res = self.client.get(SAVE_MONEY_TARGET_URL)

        save_money_target = SaveMoneyTarget.objects.all()
        serializer = SaveMoneyTargetSerializer(save_money_target, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_month_target(self):
        """Test creating a new month target"""
        payload = {'income': 1000000, 'outcome': 2000, 'month': datetime.now().month, 'year': datetime.now().year}

        res = self.client.post(MONTH_TARGET_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        exists = MonthTarget.objects.filter(
            user=self.user,
            income=payload['income'],
            outcome=payload['outcome'],
            month=payload['month'],
            year=payload['year']
        ).exists()

        self.assertTrue(exists)

    def test_create_save_money_target(self):
        """Test creating a new save money target"""
        category = Category.objects.create(user=self.user, name='test category')
        payload = {'target': 1000000, 'category': category.id}

        res = self.client.post(SAVE_MONEY_TARGET_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        exists = SaveMoneyTarget.objects.filter(
            user=self.user,
            target=payload['target'],
        ).exists()

        self.assertTrue(exists)

    def test_create_month_target_invalid(self):
        """Test creating a new month target with invalid payload"""
        payload = {'target': ''}

        res = self.client.post(MONTH_TARGET_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_save_money_target_invalid(self):
        """Test creating a new save money target with invalid payload"""
        payload = {'target': ''}

        res = self.client.post(SAVE_MONEY_TARGET_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_partial_update_month_target(self):
        """Test updating a month target with patch"""
        month_target = MonthTarget.objects.create(user=self.user, income=1000000, outcome=1000, month=datetime.now().month, year = datetime.now().year)
        payload = {'income': 2000000}

        url = reverse('accounting:month_target-detail', args=[month_target.id])
        res = self.client.patch(url, payload)

        month_target.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(month_target.income, payload['income'])
        self.assertEqual(month_target.outcome, 1000)

    def test_partial_update_save_money_target(self):
        """Test updating a save money target with patch"""
        category = Category.objects.create(user=self.user, name='test category')
        save_money_target = SaveMoneyTarget.objects.create(user=self.user, target=1000000, category=category)
        payload = {'target': 2000000}

        url = reverse('accounting:save_money_target-detail', args=[save_money_target.id])
        res = self.client.patch(url, payload)

        save_money_target.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(save_money_target.target, payload['target'])

    def test_full_update_month_target(self):
        """Test updating a month target with put"""
        month_target = MonthTarget.objects.create(user=self.user, income=1000000, outcome=20000, month=datetime.now().month, year = datetime.now().year)
        payload = {'income': 2000000, 'outcome': 2000, 'month': datetime.now().month, 'year': datetime.now().year}

        url = reverse('accounting:month_target-detail', args=[month_target.id])
        res = self.client.put(url, payload)

        month_target.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(month_target.income, payload['income'])
        self.assertEqual(month_target.outcome, payload['outcome'])

    def test_full_update_save_money_target(self):
        """Test updating a save money target with put"""
        category = Category.objects.create(user=self.user, name='test category')
        save_money_target = SaveMoneyTarget.objects.create(user=self.user, target=1000000, category=category)
        new_category = Category.objects.create(user=self.user, name='new category')
        payload = {'target': 2000000, 'category': new_category.id}

        url = reverse('accounting:save_money_target-detail', args=[save_money_target.id])
        res = self.client.put(url, payload)

        save_money_target.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(save_money_target.target, payload['target'])
        self.assertEqual(save_money_target.category, new_category)

    def test_delete_month_target(self):
        """Test deleting a month target"""
        month_target = MonthTarget.objects.create(user=self.user, income=1000000, outcome=20000, month=datetime.now().month, year = datetime.now().year)

        url = reverse('accounting:month_target-detail', args=[month_target.id])
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_save_money_target(self):
        """Test deleting a save money target"""
        category = Category.objects.create(user=self.user, name='test category')
        save_money_target = SaveMoneyTarget.objects.create(user=self.user, target=1000000, category=category)

        url = reverse('accounting:save_money_target-detail', args=[save_money_target.id])
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_month_target_invalid(self):
        """Test deleting a month target with invalid id"""
        url = reverse('accounting:month_target-detail', args=[999])
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_save_money_target_invalid(self):
        """Test deleting a save money target with invalid id"""
        url = reverse('accounting:save_money_target-detail', args=[999])
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_month_target_not_owned(self):
        """Test deleting a month target not owned"""
        month_target = MonthTarget.objects.create(user=create_user(account='testaccount2', password='testpass'), income=1000000, outcome=2000, month=datetime.now().month, year = datetime.now().year)

        url = reverse('accounting:month_target-detail', args=[month_target.id])
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_save_money_target_not_owned(self):
        """Test deleting a save money target not owned"""
        user2 = create_user(account='testaccount2', password='testpass')
        category = Category.objects.create(user=user2, name='test category')
        save_money_target = SaveMoneyTarget.objects.create(user=user2, target=1000000, category=category)

        url = reverse('accounting:save_money_target-detail', args=[save_money_target.id])
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_month_target_not_owned(self):
        """Test updating a month target not owned"""
        month_target = MonthTarget.objects.create(user=create_user(account='testaccount2', password='testpass'), income=1000000, outcome=500, month=datetime.now().month, year = datetime.now().year)
        payload = {'income': 2000000, 'outcome': 1000, 'month': datetime.now().month, 'year': datetime.now().year}

        url = reverse('accounting:month_target-detail', args=[month_target.id])
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_save_money_target_not_owned(self):
        """Test updating a save money target not owned"""
        user2 = create_user(account='testaccount2', password='testpass')
        category = Category.objects.create(user=user2, name='test category')
        save_money_target = SaveMoneyTarget.objects.create(user=user2, target=1000000, category=category)
        new_category = Category.objects.create(user=user2, name='new category')
        payload = {'target': 2000000, 'category': new_category.id}

        url = reverse('accounting:save_money_target-detail', args=[save_money_target.id])
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_month_target_by_year_and_month(self):
        """Test get month target by year and month"""
        month_target = MonthTarget.objects.create(user=self.user, income=1000000, outcome=500, month=datetime.now().month, year = datetime.now().year)

        url = reverse('accounting:month-target-detail', args=[month_target.year, month_target.month])
        res = self.client.get(url)

        serializer = MonthTargetSerializer(month_target)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
