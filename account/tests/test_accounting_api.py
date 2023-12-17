"""
Test cases for the accounting API
"""
from datetime import datetime, date , timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Accounting

from account.serializers import AccountingSerializer, AccountingDetailSerializer


ACCOUNTING_URL = reverse('accounting:accounting-list')


def detail_url(accounting_id):
    """Return accounting detail URL"""
    return reverse('accounting:accounting-detail', args=[accounting_id])


def create_accounting(user, **params):
    """Helper function to create an accounting object"""
    default = {
        'date': datetime.now().strftime("%Y-%m-%d"),
        'type': 'income',
        'amount': 1000,
    }
    default.update(params)

    return Accounting.objects.create(user=user, **default)


class PublicAccountingApiTests(TestCase):
    """Test the publicly available accounting API"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that auth is required for retrieving accounting"""
        res = self.client.get(ACCOUNTING_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateAccountingApiTests(TestCase):
    """Test the authorized user accounting API"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'testaccount',
            'password123',
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_accounting(self):
        """Test retrieving a list of accounting"""
        create_accounting(user=self.user)
        create_accounting(user=self.user)

        res = self.client.get(ACCOUNTING_URL)

        accounting = Accounting.objects.all().order_by('-date')
        serializer = AccountingSerializer(accounting, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_accounting_limit_to_user(self):
        """Test that accounting returned are for the authenticated user"""
        user2 = get_user_model().objects.create_user(
            'testaccount2',
            'password123',
        )
        create_accounting(user=user2)
        acc2=create_accounting(user=self.user)

        res = self.client.get(ACCOUNTING_URL)

        accounting = Accounting.objects.filter(user=self.user)
        serializer = AccountingSerializer(accounting, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_accounting_detail(self):
        """Test get a accounting detail"""
        accounting = create_accounting(user=self.user)

        url = detail_url(accounting.id)
        res = self.client.get(url)

        serializer = AccountingDetailSerializer(accounting)
        self.assertEqual(res.data, serializer.data)

    def test_create_accounting(self):
        """Test creating a new accounting is successful"""
        payload = {
            'date': datetime.now().strftime("%Y-%m-%d"),
            'type': 'income',
            'amount': 1000,
        }
        res = self.client.post(ACCOUNTING_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        accounting = Accounting.objects.get(id=res.data['id'])
        for k, v in payload.items():
            if k == 'date':
                date_obj = datetime.strptime(v, '%Y-%m-%d').date()
                self.assertEqual(date_obj, getattr(accounting, k))
            else:
                self.assertEqual(v, getattr(accounting, k))
        self.assertEqual(accounting.user, self.user)

    def test_retrieve_accounting_by_date_range(self):
        """Test retrieving accounting records by date range"""
        create_accounting(self.user, date='2021-01-10', type='income', amount=1000)
        create_accounting(self.user, date='2021-01-20', type='outcome', amount=500)
        create_accounting(self.user, date='2021-02-01', type='income', amount=1500)

        params = {
            'from': '2021-01-01',
            'end': '2021-01-31'
        }
        res = self.client.get(ACCOUNTING_URL, params)

        accounting_within_range = Accounting.objects.filter(
            user=self.user,
            date__range=[params['from'], params['end']]
        ).order_by('-date')
        serializer = AccountingSerializer(accounting_within_range, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_current_month_accounting(self):
        """Test retrieving current month's accounting records"""
        now = datetime.now()
        first_day = now.replace(day=1)

        if now.month == 12:
            next_month = now.replace(year=now.year + 1, month=1, day=1)
        else:
            next_month = now.replace(month=now.month + 1, day=1)

        last_day = next_month - timedelta(days=1)

        create_accounting(self.user, date=first_day, type='income', amount=1200)
        create_accounting(self.user, date=last_day, type='income', amount=1500)
        create_accounting(self.user, date=first_day - timedelta(days=1), type='outcome', amount=500)
        create_accounting(self.user, date=last_day + timedelta(days=1), type='outcome', amount=1500)

        res = self.client.get(ACCOUNTING_URL)

        current_month_accounting = Accounting.objects.filter(
            user=self.user,
            date__range=[first_day, last_day]
        ).order_by('-date')
        serializer = AccountingSerializer(current_month_accounting, many=True)


        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_partial_update_accounting(self):
        """Test updating a accounting with patch"""
        accounting = create_accounting(user=self.user)
        payload = {
            'amount': 2000,
        }
        id = accounting.id
        url = detail_url(accounting.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        accounting.refresh_from_db()
        self.assertEqual(accounting.amount, payload['amount'])
        self.assertEqual(accounting.id, id)
        self.assertEqual(accounting.user, self.user)

    def test_full_update_accounting(self):
        """Test updating a accounting with put"""
        accounting = create_accounting(
            user=self.user,
            date=datetime.now().strftime("%Y-%m-%d"),
            type='income',
            amount=1000
        )

        payload = {
            'date': datetime.now().strftime("%Y-%m-%d"),
            'type': 'outcome',
            'amount': 2000,
        }
        url = detail_url(accounting.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        accounting.refresh_from_db()
        for k, v in payload.items():
            if k == 'date':
                date_obj = datetime.strptime(v, '%Y-%m-%d').date()
                self.assertEqual(date_obj, getattr(accounting, k))
            else:
                self.assertEqual(v, getattr(accounting, k))
        self.assertEqual(accounting.user, self.user)

    def test_update_user_return_error(self):
        """Test updating accounting entry for another user returns an error"""
        other_user = get_user_model().objects.create_user('otheraccount', 'testpass123')
        accounting = create_accounting(user=other_user)

        payload = {'user' : self.user, 'type': 'outcome'}
        url = detail_url(accounting.id)
        res = self.client.patch(url, payload)

        accounting.refresh_from_db()
        self.assertNotEqual(accounting.user, payload['user'])
        self.assertNotEqual(accounting.type, 'outcome')
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_accounting(self):
        """Test deleting a accounting"""
        accounting = create_accounting(user=self.user)

        url = detail_url(accounting.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Accounting.objects.filter(id=accounting.id).exists())

    def test_accounting_other_users_delete(self):
        """Test deleting a accounting of another user returns an error"""
        other_user = get_user_model().objects.create_user('otheraccount', 'testpass123')
        accounting = create_accounting(user=other_user)

        url = detail_url(accounting.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Accounting.objects.filter(id=accounting.id).exists())

    def test_accounting_type_validation(self):
        """Test that accounting type is validated"""
        payload = {
            'date': datetime.now().strftime("%Y-%m-%d"),
            'type': 'invalid',
            'amount': 1000,
        }
        res = self.client.post(ACCOUNTING_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(Accounting.objects.filter(type=payload['type']).exists())