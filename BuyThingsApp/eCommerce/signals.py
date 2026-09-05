from django.contrib.auth.models import Group, Permission


def sync_group_permissions(sender, **kwargs):
    """Create/update the Vendor and Buyer groups and assign their eCommerce permissions.

    Connected to the post_migrate signal, so this runs automatically after
    every migration to keep the two groups' permission sets up to date.
    """
    app_label = "eCommerce"  # verify this matches your actual app_label — see note below

    vendor_codenames = [
        "add_products", "change_products", "delete_products", "view_products",
        "add_stores", "change_stores", "delete_stores", "view_stores",
        "view_reviews",
    ]
    buyer_codenames = [
        "view_products", "view_stores", "view_reviews",
        "add_reviews", "change_reviews", "delete_reviews",
        "buy_products",
    ]

    vendors, _ = Group.objects.get_or_create(name="Vendor")
    vendors.permissions.set(
        Permission.objects.filter(content_type__app_label=app_label, codename__in=vendor_codenames)
    )

    buyers, _ = Group.objects.get_or_create(name="Buyer")
    buyers.permissions.set(
        Permission.objects.filter(content_type__app_label=app_label, codename__in=buyer_codenames)
    )
