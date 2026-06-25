from pathlib import Path

from django.conf import settings
from django.core.management import BaseCommand, CommandError, call_command
from django.core.management.color import no_style
from django.db import connection

from apps.accounts.models import User
from apps.catalog.models import Category, Favorite, Product
from apps.feedback.models import ContactRequest
from apps.orders.models import Order, OrderItem


class Command(BaseCommand):
    help = "Loads the project fixture into an empty database and resets sequences."

    def add_arguments(self, parser):
        parser.add_argument("--fixture", default="project_data.json")
        parser.add_argument("--force", action="store_true")

    def handle(self, *args, **options):
        fixture_name = options["fixture"]
        fixture_path = Path(settings.BASE_DIR) / "fixtures" / fixture_name

        if not fixture_path.exists():
            raise CommandError(f"Fixture not found: {fixture_path}")

        tracked_models = [
            User,
            Category,
            Product,
            Favorite,
            Order,
            OrderItem,
            ContactRequest,
        ]
        counts = {
            model._meta.label: model.objects.count()
            for model in tracked_models
        }

        if any(counts.values()) and not options["force"]:
            summary = ", ".join(
                f"{label}={count}"
                for label, count in counts.items()
                if count
            )
            self.stdout.write(
                self.style.WARNING(
                    f"Skipped fixture load because the database already has data: {summary}"
                )
            )
            return

        call_command("loaddata", str(fixture_path))
        self._reset_sequences(tracked_models)
        self.stdout.write(self.style.SUCCESS("Project data fixture loaded successfully."))

    def _reset_sequences(self, models):
        statements = connection.ops.sequence_reset_sql(no_style(), models)
        with connection.cursor() as cursor:
            for statement in statements:
                cursor.execute(statement)
