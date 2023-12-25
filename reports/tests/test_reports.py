""""
Test for reports
"""

'''
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from core.models import Accounting, Category

import json
import os
import tempfile
from datetime import datetime


def create_user(account='testaccount', password='testpass123', name='testuser'):
    """Helper function to create a user"""
    return get_user_model().objects.create_user(account, password, name=name)


class PublicReportsApiTests(TestCase):
    """Test the publicly available reports API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required for retrieving reports"""
        res = self.client.get(reverse('reports:get_month_reports', args=[datetime.now().year, datetime.now().month]))

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateReportsApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)

    def test_retrieve_monthly_report(self):
        """Test retrieving a list of reports"""
        Accounting.objects.create(
            user=self.user,
            date=datetime.now(),
            type='income',
            amount=100,
            title='test title'
        )
        Accounting.objects.create(
            user=self.user,
            date=datetime.now(),
            type='outcome',
            amount=200,
            title='test title'
        )

        res = self.client.get(reverse('reports:get_month_reports', args=[datetime.now().year, datetime.now().month]))

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)

    def test_retrieve_yearly_report(self):
        """Test retrieving a list of reports"""
        Accounting.objects.create(
            user=self.user,
            date=datetime.now(),
            type='income',
            amount=100,
            title='test title'
        )
        Accounting.objects.create(
            user=self.user,
            date=datetime.now(),
            type='outcome',
            amount=200,
            title='test title'
        )

        res = self.client.get(reverse('reports:get_year_reports', args=[datetime.now().year]))

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)
'''