from django.db import models
from authemail.models import EmailAbstractUser, EmailUserManager

class User(EmailAbstractUser):
    """
    Basis: E-Mail als Login-Feld.
    Du kannst hier beliebige Extra-Felder ergänzen, z. B. avatar = models.ImageField(...)
    """
    # Beispiel eines Zusatzfeldes:
    # display_name = models.CharField(max_length=50, blank=True)

    # Manager MUSS gesetzt sein
    objects = EmailUserManager()

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
