from django.apps import AppConfig
from django.db.models.signals import post_migrate


class ECommerceConfig(AppConfig):
    """Application configuration for the eCommerce app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "eCommerce"  # must match your app's actual dotted path

    def ready(self):
        """Connect the post_migrate signal so group permissions are synced after migrations run."""
        from .signals import sync_group_permissions
        post_migrate.connect(sync_group_permissions, sender=self)
