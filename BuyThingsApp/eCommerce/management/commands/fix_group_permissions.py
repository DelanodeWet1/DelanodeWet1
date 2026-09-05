from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission


class Command(BaseCommand):
    help = (
        "Patches the Vendor and Buyer groups with the correct eCommerce permissions. "
        "Safe to run multiple times — it only sets permissions, it doesn't touch users "
        "or duplicate groups. Use this to repair groups that were created before the "
        "codename__in filter bug in register_user was fixed."
    )

    def handle(self, *args, **options):
        app_label = "eCommerce"  # Adjust if manage.py shell shows a different app_label

        vendor_codenames = [
            "add_products", "change_products", "delete_products", "view_products",
            "add_stores", "change_stores", "delete_stores", "view_stores",
            "view_reviews",
        ]
        buyer_codenames = [
            "view_products", "view_stores", "view_reviews",
            "add_reviews", "change_reviews", "delete_reviews",
        ]

        self._sync_group("Vendor", app_label, vendor_codenames)
        self._sync_group("Buyer", app_label, buyer_codenames)

        self.stdout.write(self.style.SUCCESS("Group permissions successfully patched."))

    def _sync_group(self, group_name, app_label, codenames):
        group, created = Group.objects.get_or_create(name=group_name)

        perms = Permission.objects.filter(
            content_type__app_label=app_label,
            codename__in=codenames,
        )

        found_codenames = set(perms.values_list("codename", flat=True))
        missing = set(codenames) - found_codenames
        if missing:
            self.stdout.write(
                self.style.WARNING(
                    f"[{group_name}] Could not find these codenames under app_label "
                    f"'{app_label}': {sorted(missing)}. Double check the app_label and "
                    f"codenames match what's in your database."
                )
            )

        group.permissions.set(perms)  # replaces existing perms with exactly this set

        status = "created" if created else "updated"
        self.stdout.write(
            f"[{group_name}] group {status}, now has {perms.count()} permission(s)."
        )
