from django.db import models
from django.contrib.auth.models import BaseUserManager
from django.db.models.expressions import Value
from task import settings as SETTINGS

class UserQuerySet(models.query.QuerySet):
  def get_by_name(self, first_name):
    return self.filter(first_name=first_name, role__in = (SETTINGS.USER_ROLE, SETTINGS.MANAGER_ROLE))

class UserInactiveManager(models.Manager):
    def get_queryset(self):
        ''' get inactive users '''
        return super().get_queryset().filter(is_active=False)

class UserAllManager(models.Manager):
    def get_queryset(self):
        ''' get inactive users '''
        return super().get_queryset().filter(role__in = (SETTINGS.USER_ROLE, SETTINGS.MANAGER_ROLE))


class UserManager(BaseUserManager):
    def create_user(self, email, password):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        if not password:
            raise Value('Please provide a valid password')

        user = self.model(
            email=self.normalize_email(email),
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """
        Creates and saves a superuser with the given email and password.
        """
        user = self.create_user(
            email,
            password=password,
        )
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user

    def get_full_name(self):
        pass

    def get_short_name(self):
        pass

    @property
    def is_superuser(self):
        return self.is_admin

    @property
    def is_staff(self):
       return self.is_admin

    # def has_perm(self, perm, obj=None):
    #    return self.is_admin

    # def has_module_perms(self, app_label):
    #    return self.is_admin

    @is_staff.setter
    def is_staff(self, value):
        self._is_staff = value

    def get_queryset(self):
        return UserQuerySet(self.model, using=self._db)

    def get_by_name(self, first_name):
        return self.get_queryset().get_by_name(first_name)

    def get_queryset(self):
        ''' get active users '''
        return super().get_queryset().filter(is_active=True)
