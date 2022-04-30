import uuid

from django.db import models
from django.contrib.auth.models import AbstractUser 


from ..managers.usermanager import UserManager, UserInactiveManager,UserAllManager

class User(AbstractUser):
    full_name = models.CharField(blank=True, null=True, max_length=100)
    name = models.CharField(blank=True, null=True, max_length=100)
    email = models.EmailField(('email address'), unique=True)
    phone_no = models.CharField(blank=True, null=True, max_length=15)
    is_active = models.BooleanField(default=True)
    role = models.CharField(max_length=50, default="user")
    

    username = None
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['password']

    objects = UserManager()
    inactive = UserInactiveManager()
    allusers= UserAllManager()
    class Meta:
        db_table = "users"

    def __str__(self):
        return self.email

        # Here's where to take a look
    def soft_delete(self):
        self.is_active = False
        self.save()

