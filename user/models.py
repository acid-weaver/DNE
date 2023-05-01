from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

from utils.models import TimeStamps


class CustomUserManager(BaseUserManager):
    '''
    Custom users manager class for project scalability.
    '''

    def _create_user(self, username, password, **extra_fields):
        if not username:
            raise ValueError("Username must be provided")
        if not password:
            raise ValueError('Password is not provided')

        user = self.model(
            username = username,
            **extra_fields
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, password, **extra_fields):
        extra_fields.setdefault('is_staff',True)
        extra_fields.setdefault('is_active',True)
        extra_fields.setdefault('is_superuser',False)
        return self._create_user(username, password, **extra_fields)

    def create_superuser(self, username, password, **extra_fields):
        extra_fields.setdefault('is_staff',True)
        extra_fields.setdefault('is_active',True)
        extra_fields.setdefault('is_superuser',True)
        return self._create_user(username, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin, TimeStamps):
    '''
    Custom user class for project scalability.
    '''

    username = models.CharField(db_index=True, unique=True, max_length=255)

    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)

    is_staff = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
