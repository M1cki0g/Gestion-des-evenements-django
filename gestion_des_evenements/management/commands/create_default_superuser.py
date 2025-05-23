from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Creates a default superuser for admin access'

    def handle(self, *args, **options):
        User = get_user_model()
        admin_username = os.getenv('DJANGO_ADMIN_USERNAME', 'admin')
        admin_email = os.getenv('DJANGO_ADMIN_EMAIL', 'admin@example.com')
        admin_password = os.getenv('DJANGO_ADMIN_PASSWORD', 'admin123')

        if User.objects.filter(username=admin_username).exists():
            self.stdout.write(self.style.WARNING(f'Superuser "{admin_username}" already exists'))
            return

        try:
            User.objects.create_superuser(
                username=admin_username,
                email=admin_email,
                password=admin_password
            )
            self.stdout.write(self.style.SUCCESS(f'Superuser "{admin_username}" created successfully'))
            logger.info(f'Superuser "{admin_username}" created successfully')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Failed to create superuser: {e}'))
            logger.error(f'Failed to create superuser: {e}')
