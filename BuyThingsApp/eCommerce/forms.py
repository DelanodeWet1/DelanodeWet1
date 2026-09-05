from django import forms
from .models import Review, Store, Product


class ProductForm(forms.ModelForm):
    """Form for creating and updating Product objects.
    Fields:
    - name: CharField for the product name.
    - description: TextField for the product description.
    - price: DecimalField for the product price.
    - stock: PositiveIntegerField for the product stock.

    Meta class:
    - Defines the model to use (Product) and the fields to include in the form.
    :param forms.ModelForm: Django's ModelForm class.
    """

    class Meta:
        model = Product
        fields = ["name", "description", "price", "stock"]

       
class StoreForm(forms.ModelForm):
    """Form for creating and updating Store objects.
    Fields:
    - name: CharField for the store name.
    - description: TextField for the store description.

    Meta class:
    - Defines the model to use (Store) and the fields to include in the form.
    :param forms.ModelForm: Django's ModelForm class.
    """

    class Meta:
        model = Store
        fields = ["name", "description"]

        
class ReviewForm(forms.ModelForm):
    """Form for creating and updating Product objects.
    Fields:
    - title: CharField for the review title.
    - body: TextField for the review body.

    Meta class:
    - Defines the model to use (Review) and the fields to include in the form.
    :param forms.ModelForm: Django's ModelForm class.
    """

    class Meta:
        model = Review
        fields = ["title", "body", "rating"]
