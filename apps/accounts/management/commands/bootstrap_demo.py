from django.contrib.auth import get_user_model
from django.core.management import BaseCommand, call_command


User = get_user_model()


def build_username(email):
    return email.split("@", 1)[0].replace(".", "_")


class Command(BaseCommand):
    help = "Seeds demo catalog data and ensures a working admin account."

    def add_arguments(self, parser):
        parser.add_argument("--email", default="admin@gmail.com")
        parser.add_argument("--password", default="admin123")
        parser.add_argument("--name", default="Admin")

    def handle(self, *args, **options):
        email = options["email"].strip().lower()
        password = options["password"]
        name = options["name"].strip() or "Admin"

        call_command("seed_demo_data")

        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "username": build_username(email),
                "name": name,
            },
        )

        if not user.username:
            user.username = build_username(email)

        user.name = name
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.set_password(password)
        user.save()

        action = "created" if created else "updated"
        self.stdout.write(
            self.style.SUCCESS(
                f"Demo admin {action}: email={email} password={password}"
            )
        )
