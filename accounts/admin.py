from django.contrib import admin
from django.contrib.auth import get_user_model
from authemail.admin import EmailUserAdmin

User = get_user_model()

# Standard-Eintrag entfernen …
admin.site.unregister(User)
# … und mit Authemail-Admin wieder hinzufügen
admin.site.register(User, EmailUserAdmin)
