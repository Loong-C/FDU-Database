from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create or update the demo admin/operator/viewer accounts."

    DEMO_USERS = [
        ("admin", "Admin123!", "admin", "Administrator"),
        ("operator", "Operator123!", "operator", "Operator"),
        ("viewer", "Viewer123!", "viewer", "Viewer"),
    ]

    def handle(self, *args, **options):
        user_model = get_user_model()
        for username, password, role, display_name in self.DEMO_USERS:
            user, created = user_model.objects.get_or_create(
                username=username,
                defaults={
                    "role": role,
                    "display_name": display_name,
                    "is_active": True,
                },
            )
            user.role = role
            user.display_name = display_name
            user.is_active = True
            user.set_password(password)
            user.save()
            action = "Created" if created else "Updated"
            self.stdout.write(f"{action} demo user: {username}")

        self.stdout.write(self.style.SUCCESS("Demo users are ready."))
