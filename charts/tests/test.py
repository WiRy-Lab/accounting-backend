"""
Test file for charts app
"""
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from core.models import Accounting , MonthTarget, Category
from datetime import datetime, timedelta

def create_user(**params):
    """Helper function to create new user"""
    return get_user_model().objects.create_user(**params)


class PublicChartsApiTests(TestCase):
    """
    Test the publically available charts API
    """
    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """
        Test that login is required for retrieving charts
        """
        res = self.client.get(reverse('charts:range_cost'))
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateChartsApiTests(TestCase):
    """
    Test the authorized user charts API
    """
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

    def test_retrieve_charts(self):
        """
        Test retrieving charts
        """
        payload = {
            'date': datetime.now().strftime("%Y-%m-%d"),
            'type': 'income',
            'amount': 10000,
            'title': 'test title',
            'description': 'test description',
        }
        Accounting.objects.create(user=self.user, **payload)
        payload = {
            'date': datetime.now().strftime("%Y-%m-%d"),
            'type': 'outcome',
            'amount': 20000,
            'title': 'test title',
            'description': 'test description',
        }
        Accounting.objects.create(user=self.user, **payload)
        payload = {
            'date': (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
            'type': 'income',
            'amount': 10000,
            'title': 'test title',
            'description': 'test description',
        }
        Accounting.objects.create(user=self.user, **payload)
        payload = {
            'date': (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
            'type': 'outcome',
            'amount': 20000,
            'title': 'test title',
            'description': 'test description',
        }
        Accounting.objects.create(user=self.user, **payload)
        payload = {
            'date': (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d"),
            'type': 'outcome',
            'amount': 50000,
            'title': 'test title',
            'description': 'test description',
        }
        Accounting.objects.create(user=self.user, **payload)
        payload = {
            'date': (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d"),
            'type': 'outcome',
            'amount': 30000,
            'title': 'test title',
            'description': 'test description',
        }
        Accounting.objects.create(user=self.user, **payload)


        from_date = datetime.now().strftime('%Y-%m-%d')
        end_date = (datetime.now() + timedelta(days=6)).strftime('%Y-%m-%d')
        payload = {
            'from': from_date,
            'end': end_date,
        }
        res = self.client.get(reverse('charts:range_cost'), payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['from'], from_date)
        self.assertEqual(res.data['end'], end_date)

    def test_retrieve_charts_invalid_range(self):
        """
        Test retrieving charts with invalid range
        """
        from_date = datetime.now().strftime('%Y-%m-%d')
        end_date = (datetime.now() + timedelta(days=0)).strftime('%Y-%m-%d')
        payload = {
            'from': from_date,
            'end': end_date,
        }
        res = self.client.get(reverse('charts:range_cost'), payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_other_user_charts(self):
        """
        Test retrieving charts for other user
        """
        user2 = create_user(
            account='apiccount2',
            password='testpass123',
        )
        payload = {
            'date': datetime.now().strftime("%Y-%m-%d"),
            'type': 'income',
            'amount': 10000,
            'title': 'test title',
            'description': 'test description',
        }
        Accounting.objects.create(user=user2, **payload)
        payload = {
            'date': datetime.now().strftime("%Y-%m-%d"),
            'type': 'outcome',
            'amount': 20000,
            'title': 'test title',
            'description': 'test description',
        }
        Accounting.objects.create(user=user2, **payload)

        from_date = datetime.now().strftime('%Y-%m-%d')
        end_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        payload = {
            'from': from_date,
            'end': end_date,
        }
        res = self.client.get(reverse('charts:range_cost'), payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['from'], from_date)
        self.assertEqual(res.data['end'], end_date)
        self.assertEqual(res.data['income'], [0, 0])
        self.assertEqual(res.data['outcome'], [0, 0])

    def test_retrieve_target(self):
        """Test retrieving month target"""
        payload = {
            'date': datetime.now().strftime("%Y-%m-%d"),
            'type': 'outcome',
            'amount': 10000,
            'title': 'test title',
            'description': 'test description',
        }
        Accounting.objects.create(user=self.user, **payload)
        payload = {
            'date': (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
            'type': 'outcome',
            'amount': 20000,
            'title': 'test title',
            'description': 'test description',
        }
        Accounting.objects.create(user=self.user, **payload)
        payload = {
            'date': (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d"),
            'type': 'income',
            'amount': 50000,
            'title': 'test title',
            'description': 'test description',
        }
        Accounting.objects.create(user=self.user, **payload)

        MonthTarget.objects.create(user=self.user, year=datetime.now().year, month=datetime.now().month, income=100000, outcome=100000)

        res = self.client.get(reverse('charts:target', args=[datetime.now().year, datetime.now().month]))

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['year'], datetime.now().year)
        self.assertEqual(res.data['month'], datetime.now().month)
        self.assertEqual(res.data['target_income'], 100000)
        self.assertEqual(res.data['target_outcome'], 100000)
        self.assertEqual(res.data['income'][0], 50000)
        self.assertEqual(res.data['income'][1], 50000)
        self.assertEqual(res.data['outcome'][0], 30000)
        self.assertEqual(res.data['outcome'][1], 70000)

    def test_retrieve_type_cost(self):
        """Test retrieving type cost"""
        payload = {
            'date': datetime.now().strftime("%Y-%m-%d"),
            'type': 'outcome',
            'amount': 10000,
            'title': 'test title',
            'description': 'test description',
        }
        accounting = Accounting.objects.create(user=self.user, **payload)
        accounting.category.add(Category.objects.create(user=self.user, name='食'))
        payload = {
            'date': (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
            'type': 'outcome',
            'amount': 20000,
            'title': 'test title',
            'description': 'test description',
        }
        accounting = Accounting.objects.create(user=self.user, **payload)
        accounting.category.add(Category.objects.create(user=self.user, name='衣'))
        payload = {
            'date': (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d"),
            'type': 'outcome',
            'amount': 40000,
            'title': 'test title',
            'description': 'test description',
        }
        accounting = Accounting.objects.create(user=self.user, **payload)
        accounting.category.add(Category.objects.create(user=self.user, name='住'))
        payload = {
            'date': (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d"),
            'type': 'income',
            'amount': 50000,
            'title': 'test title',
            'description': 'test description',
        }
        Accounting.objects.create(user=self.user, **payload)

        payload = {
            'from': datetime.now().strftime('%Y-%m-%d'),
            'end': (datetime.now() + timedelta(days=6)).strftime('%Y-%m-%d'),
        }
        res = self.client.get(reverse('charts:type_cost'), payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['from'], datetime.now().strftime('%Y-%m-%d'))
        self.assertEqual(res.data['end'], (datetime.now() + timedelta(days=6)).strftime('%Y-%m-%d'))
        self.assertEqual(res.data['data'][2]['name'], '食')
        self.assertEqual(res.data['data'][2]['percent'], '14%')
        self.assertEqual(res.data['data'][2]['data'], [14, 86])
        self.assertEqual(res.data['data'][1]['name'], '衣')
        self.assertEqual(res.data['data'][1]['percent'], '29%')
        self.assertEqual(res.data['data'][1]['data'], [29, 71])
        self.assertEqual(res.data['data'][0]['name'], '住')
        self.assertEqual(res.data['data'][0]['percent'], '57%')
        self.assertEqual(res.data['data'][0]['data'], [57, 43])


