"""
Database models
"""
from typing import Any
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

    def create_superuser(self, account, password):
        """Create, save and return a new superuser"""
        user = self.create_user(account, password)
        user.is_superuser = True
        user.save(using=self._db)

        return user

class User(AbstractBaseUser, PermissionsMixin):
    """User in the system"""
    name = models.CharField(max_length=255)
    account = models.CharField(max_length=255, unique=True)
    email = models.EmailField(max_length=255)
    is_active = models.BooleanField(default=True)

    objects = UserManager()

    USERNAME_FIELD = 'account'

