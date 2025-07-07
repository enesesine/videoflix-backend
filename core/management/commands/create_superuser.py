# core/management/commands/create_superuser.py
"""
Management command:  `python manage.py create_superuser`

Creates a single super-user from the environment variables
`DJANGO_SUPERUSER_USERNAME`, `DJANGO_SUPERUSER_EMAIL`,
and `DJANGO_SUPERUSER_PASSWORD`.

If a user with the given username already exists, the command
does nothing (idempotent).
"""
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Django management command that runs on container / project start-up
    to ensure a super-user is present.
    """

    help = "Create an initial super-user from environment variables."

    def handle(self, *args, **options):
        User = get_user_model()

        username = settings.DJANGO_SUPERUSER_USERNAME
        email    = settings.DJANGO_SUPERUSER_EMAIL
        password = settings.DJANGO_SUPERUSER_PASSWORD

        # Abort if required variables are missing.
        if not username or not password:
            self.stderr.write(
                self.style.ERROR(
                    "Environment variables for the super-user are missing – skipping."
                )
            )
            return

        # Do nothing if the user already exists (idempotent).
        if User.objects.filter(username=username).exists():
            self.stdout.write(f"• Super-user '{username}' already exists – skipping.")
            return

        # Create the super-user.
        User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
        )
        self.stdout.write(self.style.SUCCESS(f"✔ Super-user '{username}' created."))
