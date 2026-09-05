from django.db import models
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator


class Product(models.Model):
    """A product listed for sale."""

    name = models.CharField(max_length=100)
    # The name of the product, like "T-shirt" or "Laptop"

    description = models.TextField(blank=True)
    # A longer description of the product; it’s optional (can be empty)

    price = models.DecimalField(max_digits=10, decimal_places=2)
    # The price of the product, with up to 10 digits total and 2 decimal places for cents

    stock = models.PositiveIntegerField()
    # How many items are available in stock (only positive numbers allowed)

    # Foreignkey relationship to the store the object is in
    store = models.ForeignKey("Store", on_delete=models.CASCADE , related_name='products', null=True, blank=True)

    def __str__(self):
        """Return the product's name, used for admin and debug display."""
        # This makes it easier to see the product’s name when printing or in admin pages
        return self.name

    class Meta:
        """Defines custom permissions for managing products."""
        # These are special permissions for users who can add, change, delete, or view products
        permissions = [
            ("add_products", "Can add products"),
            ("change_products", "Can change products"),
            ("delete_products", "Can delete products"),
            ("view_products", "Can view products"),
            ("buy_products", "Can buy products"),
        ]


class Store(models.Model):
    """A store owned by a vendor, containing zero or more products."""

    name = models.CharField(max_length=100)

    description = models.TextField(blank=True)

    # Foreignkey relationship with the vendor that created the store
    vendor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE, related_name='stores', null=True, blank=True
    )

    def __str__(self):
        """Return the store's name, used for admin and debug display."""
        return self.name

    class Meta:
        """Defines custom permissions for managing stores."""
        # These are special permissions for users who can add, change, delete, or view stores
        permissions = [
            ("add_stores", "Can add stores"),
            ("change_stores", "Can change stores"),
            ("delete_stores", "Can delete stores"),
            ("view_stores", "Can view stores"),
        ]


class Review(models.Model):
    """A review written by a user about a specific product."""

    title = models.CharField(max_length=100)

    body = models.TextField()
    
    rating = models.PositiveIntegerField(validators=[MinValueValidator(0),
                                                     MaxValueValidator(5)],
                                         default=5)

    product = models.ForeignKey(
        "Product",
        on_delete=models.CASCADE, related_name='reviews', null=True, blank=True
    )

    # Foreignkey relationship with the vendor that created the store
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE, null=True, blank=True
    )

    verified = models.BooleanField(default=False)

    def __str__(self):
        """Return the review's title, used for admin and debug display."""
        return self.title

    class Meta:
        """Defines custom permissions for managing reviews."""
        # These are special permissions for users who can add, change, delete, or view reviews
        permissions = [
            ("add_reviews", "Can add reviews"),
            ("change_reviews", "Can change reviews"),
            ("delete_reviews", "Can delete reviews"),
            ("view_reviews", "Can view reviews"),
        ]


class Order(models.Model):
    """A record of a completed purchase of a product by a user."""

    # Foreign key relationship that links an order to the user that made the purchase
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')

    # Foreign key relationship that links an order to the product that was purchased
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='orders')

    # The quantity of the purchased product
    quantity = models.PositiveIntegerField(default=1)

    # The date at which the purchase was made
    purchased_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Return a human-readable summary of the order."""
        return f"{self.user.username} bought {self.quantity} {self.product.name}"
