"""
Database models
"""
from typing import Any
from django.conf import settings
from django.db import models
from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager, PermissionsMixin)


class UserManager(BaseUserManager):
    """Manager for user profiles"""

    def create_user(self, account, password=None, **extra_fields):
        """Create, save and return a new user"""
        if not account:
            raise ValueError('User must have an account')
        user = self.model(account=account, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, account, password=None, **extra_fields):
        """Create, save and return a new superuser"""
        if not account:
            raise ValueError('SuperUser must have an account')

        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(account, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """User in the system"""
    name = models.CharField(max_length=255)
    account = models.CharField(max_length=255, unique=True)
    email = models.EmailField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'account'


class Accounting(models.Model):
    """Accounting object"""
    TYPE_CHOICES = (
        ('income', 'income'),
        ('outcome', 'outcome'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    date = models.DateField()
    type = models.CharField(max_length=255, choices=TYPE_CHOICES)
    amount = models.IntegerField()
    category = models.ManyToManyField('Category')

    def __str__(self) -> str:
        return str(self.user) + ' ' + self.type + ' ' + str(self.amount)


class Category(models.Model):
    """Category for accounting"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.name