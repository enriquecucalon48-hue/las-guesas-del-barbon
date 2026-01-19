from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = "Create default admin user if it does not exist"

    def handle(self, *args, **kwargs):
        User = get_user_model()

        username = "admin"
        password = "karma593"
        email = "davidcorso428@gmail.com"

        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(
                username=username,
                password=password,
                email=email
            )
            self.stdout.write(self.style.SUCCESS("Admin user created"))
        else:
            self.stdout.write("Admin user already exists")