from django.db import models
from authemail.models import EmailAbstractUser, EmailUserManager

class User(EmailAbstractUser):
 
    objects = EmailUserManager()

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
