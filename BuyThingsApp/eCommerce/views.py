from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse, reverse_lazy
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.core.mail import EmailMessage
from .models import Product, Store, Review, Order
from .forms import ProductForm, ReviewForm, StoreForm
from .serializers import VendorSerializer, StoreReviewSerializer, StorePostSerializer, ProductSerializer
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import BasicAuthentication
from rest_framework.response import Response
from .functions.jsonplaceholder import get_posts



def view_product_page(request):
    """Show a search form for a product by name, or the matching product's details on submit.

    :param request: HTTP request object.
    :return: Rendered product_page.html with the found product, a not-found/permission error, or an empty search form.
    """
    user = request.user  # Get the current logged-in user

    # Check if user has permission to view products
    if user.has_perm('eCommerce.view_product') or user.has_perm('eCommerce.view_products'):
        if request.method == 'POST':
            product_name = request.POST.get('product')  # Get product name from form submission

            if not product_name:
                # If no product name given, show error on page
                return render(request, 'eCommerce/product_page.html', {
                    'error': 'No product name was given.'
                })

            try:
                # Try to find the product in the database by its name
                product = Product.objects.get(name=product_name)
                # Show product details on the page
                return render(request, 'eCommerce/product_page.html', {'product': product})
            except ObjectDoesNotExist:
                # If product not found, show error on page
                return render(request, 'eCommerce/product_page.html', {
                    'error': 'Product not found.'
                })
        
        # If page is opened normally (GET request), just show empty form
        return render(request, 'eCommerce/product_page.html')
    
    # If user does not have permission to view products, show error
    return render(request, 'eCommerce/product_page.html', {
        'error': 'You do not have permission to view this product.'
    })


@login_required(login_url=reverse_lazy('grabsomore:login'))
def product_create(request, pk):
    """View to create a new product.
    A product can only be created from a store page and
    is associated with that store.
    
    :param request: HTTP request object.
    :return: Rendered template for creating a new product.
    """
    user = request.user  # Get the currently logged-in user
    
    store = get_object_or_404(Store, pk=pk)
    
    # Check if user has permission to create products
    if user.has_perm('eCommerce.add_product') or user.has_perm('eCommerce.add_products') and (user == store.vendor):
    
        if request.method == "POST":
            form = ProductForm(request.POST)
            if form.is_valid():
                product = form.save(commit=False)
                product.store = store
                product.save()
                return redirect("eCommerce:store_detail", store.pk)
        else:
            form = ProductForm()

        return render(request, "eCommerce/product_form.html", {"form": form, "store": store,})
    
    products = store.products.all()
    # If user does not have permission, show error
    return render(request, 'eCommerce/store_detail.html', {
        "store": store,
        'products': products,
        'error': 'You do not have permission to create products.',
    })
    
    
@login_required(login_url=reverse_lazy('grabsomore:login'))
def product_update(request, pk):
    """
    View to update an existing product.

    :param request: HTTP request object.
    :param pk: Primary key of the product to be updated.
    :return: Rendered template for updating the specified product.
    """
    
    user = request.user  # Get the currently logged-in user
    product = get_object_or_404(Product, pk=pk)
    store = product.store
    # Check if user has permission to change products
    if user.has_perm('eCommerce.change_product') or user.has_perm('eCommerce.change_products')  and (user == store.vendor):

        if request.method == "POST":
            form = ProductForm(request.POST, instance=product)
            if form.is_valid():
                product = form.save(commit=False)
                product.save()
                return redirect("eCommerce:products_list")
        else:
            form = ProductForm(instance=product)

        return render(request, "eCommerce/product_form.html", {"form": form})
    reviews = product.reviews.all()
    return render(request, "eCommerce/product_detail.html", {
        "error": "You do not have permission to update products.",
        "product": product,
        "reviews": reviews,
        })

@login_required(login_url=reverse_lazy('grabsomore:login'))
def product_delete(request, pk):
    """
    View to delete an existing product.
    :param request: HTTP request object.
    :param pk: Primary key of the product to be deleted.
    :return: Redirect to the product list after deletion.
    """
    
    user = request.user  # Get the currently logged-in user
    product = get_object_or_404(Product, pk=pk)
    store = product.store
    # Check if user has permission to change products
    if user.has_perm('eCommerce.delete_product') or user.has_perm('eCommerce.delete_products')  and (user == store.vendor): 
        product.delete()
        return redirect("eCommerce:products_list")
    reviews = product.reviews.all()
    return render(request, "eCommerce/product_detail.html", {
        'product': product,
        'reviews': reviews,
        'error': 'You do not have permission to delete products.',
    })


@login_required(login_url=reverse_lazy('grabsomore:login'))
def store_list(request):
    """
    View to display a list of all stores.

    :param request: HTTP request object.
    :return: Rendered template with a list of stores.
    """
    
    user = request.user  # Get the currently logged-in user
    
    # Check if user has permission to change products
    if user.has_perm('eCommerce.view_store') or user.has_perm('eCommerce.view_stores'):
        
        stores = Store.objects.all()

        # Creating a context dictionary to pass data
        context = {
            "stores": stores,
            "page_title": "Store",
        }

        return render(request, "eCommerce/store_list.html", context)

    return render(request, "eCommerce/store_list.html", {
        'error':'You do not have permission to view stores.',
    })

@login_required(login_url=reverse_lazy('grabsomore:login'))
def store_create(request):
    """View to create a new store.
    
    :param request: HTTP request object.
    :return: Rendered template for creating a new store.
    """
    user = request.user  # Get the currently logged-in user
        
    # Check if user has permission to change products
    if user.has_perm('eCommerce.add_store') or user.has_perm('eCommerce.add_stores'):
        
        if request.method == "POST":
            form = StoreForm(request.POST)
            if form.is_valid():
                store = form.save(commit=False)
                store.vendor = user
                store.save()
                return redirect("eCommerce:store_list")
        else:
            form = StoreForm()

        return render(request, "eCommerce/store_form.html", {"form": form})
    stores = Store.objects.all()
    return render(request, "eCommerce/store_list.html", {
        "stores": stores,
        "page_title": "Store",
        "error": 'You do not have permission to create a store.'
        })


@login_required(login_url=reverse_lazy('grabsomore:login'))
def store_update(request, pk):
    """
    View to update an existing store.

    :param request: HTTP request object.
    :param pk: Primary key of the store to be updated.
    :return: Rendered template for updating the specified store.
    """
    store = get_object_or_404(Store, pk=pk)
    
    user = request.user  # Get the currently logged-in user
            
    # Check if user has permission to change stores
    if (user.has_perm('eCommerce.change_store') or user.has_perm('eCommerce.change_stores'))  and (user == store.vendor):

        if request.method == "POST":
            form = StoreForm(request.POST, instance=store)
            if form.is_valid():
                store = form.save(commit=False)
                store.save()
                return redirect("eCommerce:store_list")
        else:
            form = StoreForm(instance=store)
            return render(request, "eCommerce/store_form.html", {
            "form": form,
            "store": store,
            })
    products = store.products.all()
    return render(request, "eCommerce/store_detail.html", {
        'store': store,
        'products': products,
        'error': 'You do not have permission to edit stores.'
        
    })


@login_required(login_url=reverse_lazy('grabsomore:login'))
def store_delete(request, pk):
    """
    View to delete an existing store.
    :param request: HTTP request object.
    :param pk: Primary key of the store to be deleted.
    :return: Redirect to the store list after deletion.
    """
    store = get_object_or_404(Store, pk=pk)
    user = request.user  # Get the currently logged-in user      
    # Check if user has permission to change stores
    if (user.has_perm('eCommerce.delete_store') or user.has_perm('eCommerce.delete_stores'))  and (user == store.vendor):
        store.delete()
        return redirect("eCommerce:store_list")
    products = store.products.all()
    return render(request, "eCommerce/store_detail.html", {
        'store': store,
        'products': products,
        'error': 'You do not have permission to delete stores.'
        
    })


@login_required(login_url=reverse_lazy('grabsomore:login'))
def review_create(request, pk):
    """View to create a new review.
    
    :param request: HTTP request object.
    :return: Rendered template for creating a new review.
    """
    product = get_object_or_404(Product, pk=pk)
    user = request.user  # Get the currently logged-in user
    # Check if the product has been purchased by the user
    purchased = Order.objects.filter(user=user, product=product).exists()
    # Check if user has permission to create reviews
    if user.has_perm('eCommerce.add_review') or user.has_perm('eCommerce.add_reviews'):
        if request.method == "POST":
            form = ReviewForm(request.POST)
            if form.is_valid():
                review = form.save(commit=False)
                review.author = request.user
                review.product = product
                review.verified = purchased
                review.save()
                return redirect('eCommerce:product_detail', pk=product.pk)
        else:
            form = ReviewForm()
    
        return render(request, "eCommerce/review_form.html", {"form": form, "product": product, })
    reviews = product.reviews.all()
    return render(request, "eCommerce/product_detail.html", {
            'product': product,
            'reviews': reviews,
            'error': 'You do not have permission to create reviews.',
        })


@login_required(login_url=reverse_lazy('grabsomore:login'))
def review_update(request, pk):
    """
    View to update an existing review.

    :param request: HTTP request object.
    :param pk: Primary key of the review to be updated.
    :return: Rendered template for updating the specified review.
    """
    review = get_object_or_404(Review, pk=pk)
    user = request.user  # Get the currently logged-in user
    # Check if user has permission to change reviews
    if user.has_perm('eCommerce.change_review') or user.has_perm('eCommerce.change_reviews') and (user == review.author):

        if request.method == "POST":
            form = ReviewForm(request.POST, instance=review)
            if form.is_valid():
                review = form.save(commit=False)
                review.save()
                product = review.product
                reviews = product.reviews.all()
                return render(request, "eCommerce/product_detail.html", {
                            'product': product,
                            'reviews': reviews,
                        })
        else:
            form = ReviewForm(instance=review)
        product = review.product
        return render(request, "eCommerce/review_form.html", {"form": form,
                                                              "product": product})
    
    product = review.product
    reviews = product.reviews.all()
    return render(request, "eCommerce/product_detail.html", {
            'product': product,
            'reviews': reviews,
            'error': 'You do not have permission to create reviews.',
        })


@login_required(login_url=reverse_lazy('grabsomore:login'))
def review_delete(request, pk):
    """
    View to delete an existing review.
    :param request: HTTP request object.
    :param pk: Primary key of the review to be deleted.
    :return: Redirect to the review list after deletion.
    """
    review = get_object_or_404(Review, pk=pk)
    user = request.user  # Get the currently logged-in user
    # Check if user has permission to change reviews
    if user.has_perm('eCommerce.delete_review') or user.has_perm('eCommerce.delete_reviews') and (user == review.author):
        
        product = review.product
        review.delete()
        return redirect('eCommerce:product_detail', pk=product.pk)
        
    product = review.product
    reviews = product.reviews.all()
    return render(request, "eCommerce/product_detail.html", {
                'product': product,
                'reviews': reviews,
                'error': 'You do not have permission to delete reviews.',
            })


@login_required(login_url=reverse_lazy('grabsomore:login'))   
def product_detail(request, pk):
    """
    View to display details of a specific product.

    :param request: HTTP request object.
    :param pk: Primary key of the product.
    :return: Rendered template with details of the specified product.
    """
    user = request.user  # Get the currently logged-in user
    # Check if user has permission to change reviews
    if user.has_perm('eCommerce.view_product') or user.has_perm('eCommerce.view_products'):
        product = get_object_or_404(Product, pk=pk)
        reviews = product.reviews.all()
        return render(request, "eCommerce/product_detail.html", {
            'product': product,
            'reviews': reviews,
        })
    return render(request, "eCommerce/product_detail.html", {
                'product': product,
                'reviews': reviews,
                'error': 'You do not have permission to view products.'
            })

@login_required(login_url=reverse_lazy('grabsomore:login'))
def store_detail(request, pk):
    """
    View to display details of a specific store.

    :param request: HTTP request object.
    :param pk: Primary key of the product.
    :return: Rendered template with details of the specified store.
    """
    user = request.user  # Get the currently logged-in user
    # Check if user has permission to change reviews
    if user.has_perm('eCommerce.view_store') or user.has_perm('eCommerce.view_stores'):
        store = get_object_or_404(Store, pk=pk)
        products = store.products.all()
        return render(request, "eCommerce/store_detail.html", {
            "store": store,
            'products': products,
        })
    return render(request, "eCommerce/store_detail.html", {
            "store": store,
            'products': products,
            'error': 'You do not have permission to view stores.'
        })

@login_required(login_url=reverse_lazy('grabsomore:login'))
def review_detail(request, pk):
    """
    View to display details of a specific review.

    :param request: HTTP request object.
    :param pk: Primary key of the product.
    :return: Rendered template with details of the specified review.
    """
    review = get_object_or_404(Review, pk=pk)
    return render(request, "eCommerce/review_detail.html", {"review": review})
    
@login_required(login_url=reverse_lazy('grabsomore:login'))
def add_item_to_cart(request):
    """Add a product (and quantity) from a POST form into the session cart.

    Rejects the request if the user lacks purchase permission, or if the
    requested quantity — combined with whatever is already in the cart for
    that product — would exceed the product's available stock.

    :param request: HTTP request object; expects 'product_id' and 'quantity' POST fields.
    :return: Redirect to the cart page on success, or the product list with an error otherwise.
    """
    if not request.user.has_perm('eCommerce.buy_products'):
        products = Product.objects.all()
        return render(request, 'eCommerce/products_list.html', {
            'products': products,
            'error': 'You do not have permission to buy products.'
        })

    # Get item name and quantity from POST form submission
    product_id = request.POST.get('product_id')
    quantity = request.POST.get('quantity')

    # If either is missing, redirect to cart page without changing anything
    if not product_id or not quantity:
        return redirect('eCommerce:main_cart_page')

    try:
        # Convert quantity to integer, and set to 1 if invalid or less than 1
        quantity = int(quantity)
        if quantity < 1:
            quantity = 1
    except ValueError:
        quantity = 1

    product = get_object_or_404(Product, pk=product_id)

    # Get existing cart from session, or empty dictionary if none
    cart = request.session.get('cart', {})

    # Work out the TOTAL quantity this product would have in the cart
    existing_quantity = cart.get(product_id, 0)
    new_total_quantity = existing_quantity + quantity

    # Check that the cumulative quantity does not exceed available stock
    if new_total_quantity > product.stock:
        products = Product.objects.all()
        return render(request, 'eCommerce/products_list.html', {
            'products': products,
            'error': 'Quantity exceeds available stock.'
        })

    # Save the updated cumulative quantity for this product
    cart[product_id] = new_total_quantity

    # Save updated cart back into session so it persists
    request.session['cart'] = cart
    request.session.modified = True  # Mark session as changed

    # Redirect user to cart page after adding item
    return redirect(reverse('eCommerce:main_cart_page'))

@login_required(login_url=reverse_lazy('grabsomore:login'))
def retrieve_products(request):
    """Build a list of the products currently in the session cart, with their quantities.

    :param request: HTTP request object.
    :return: List of dicts with 'product' and 'quantity' keys for each item still in the cart.
    """
    products = []
    session = request.session

    # If cart exists in session, load products and their quantities
    if 'cart' in session:
        for product_id, quantity in session['cart'].items():
            try:
                # Get product from database by pk
                product = Product.objects.get(pk=product_id)
                # Add product and quantity as a dictionary to list
                products.append({'product': product, 'quantity': quantity})
            except Product.DoesNotExist:
                # Skip if product not found (may have been deleted)
                pass

    return products


@login_required(login_url=reverse_lazy('grabsomore:login'))
def show_user_cart(request):
    """Display the current user's cart with a subtotal per item and an overall total.

    :param request: HTTP request object.
    :return: Rendered main_cart_page.html with the cart items and total price.
    """
    
    if request.user.has_perm('eCommerce.buy_products'):
    
        # Get list of products and quantities from the session cart
        cart_items = retrieve_products(request)
        
        total_price = 0  # Start total price at zero

        # Calculate subtotal for each cart item and total price for whole cart
        for item in cart_items:
            subtotal = item['product'].price * item['quantity']
            item['subtotal'] = subtotal  # Add subtotal to item dictionary
            total_price += subtotal

        # Render cart page, passing in items and total price
        return render(request, 'eCommerce/main_cart_page.html', {
            'cart': cart_items,
            'total_price': total_price,
        })

    # Get all products from database
    products = Product.objects.all()
    # Show products list page, passing products to template and the error
    return render(request,
                    'eCommerce/products_list.html',
                    {'products': products,
                    'error': 'You do not have permission to buy products.'
                    }
                    )

@login_required(login_url=reverse_lazy('grabsomore:login'))
def list_products(request):
    """Display every product in the catalogue.

    :param request: HTTP request object.
    :return: Rendered products_list.html with all products.
    """
    # Get all products from database
    products = Product.objects.all()
    # Show products list page, passing products to template
    return render(request, 'eCommerce/products_list.html', {'products': products})


@login_required(login_url=reverse_lazy('grabsomore:login'))
def clear_cart(request):
    """Empty the current user's session cart.

    :param request: HTTP request object.
    :return: Redirect to the cart page.
    """
    if request.user.has_perm('eCommerce.buy_products'):
            
        # Empty the cart by setting session cart to empty dictionary
        request.session['cart'] = {}
        request.session.modified = True  # Mark session as changed

        # Redirect to cart page after clearing
        return redirect('eCommerce:main_cart_page')
    # Get all products from database
    products = Product.objects.all()
    # Show products list page, passing products to template and the error
    return render(request,
                    'eCommerce/products_list.html',
                    {'products': products,
                    'error': 'You do not have permission to buy products.'
                    }
                    )

@login_required(login_url=reverse_lazy('grabsomore:login'))
def check_out(request):
    """Convert the session cart into Order records, email the user an invoice, and clear the cart.

    :param request: HTTP request object.
    :return: Rendered check_out.html with the invoice items and total price.
    """
    if request.user.has_perm('eCommerce.buy_products'):
        
        # Get list of products and quantities from the session cart to put in the invoice
        invoice_items = retrieve_products(request)

        total_price = 0  # Start total price at zero
        
        # Calculate subtotal for each invoice item and total price for whole invoice
        for item in invoice_items:
            product=item['product']
            quantity=item['quantity']
                            
            # Create the order objects to track purchases outside of the user session
            Order.objects.create(
                user=request.user,
                product=product,
                quantity=quantity,
            )
            
            # Remove the purchased quantity from the product's available stock,
            product.stock = max(product.stock - quantity, 0)
            product.save()
            
            subtotal = product.price * quantity
            item['subtotal'] = subtotal  # Add subtotal to item dictionary
            total_price += subtotal
        
        # Get the user from the request
        user = request.user
        
        try:    
            # Create the content for the invoice email
            subject = "Invoice"
            user_email = user.email
            domain_email = settings.EMAIL_HOST_USER
            
            # Build email body
            lines = [f"Hi {user.username}, here is your invoice:\n"]
            for item in invoice_items:
                subtotal = item['product'].price * item['quantity']
                lines.append(f"{item['product'].name} x{item['quantity']} - R{subtotal}")
            lines.append(f"\nTotal: R{total_price}")

            body = "\n".join(lines)
            
            # Create the invoice email
            email = EmailMessage(subject, body, domain_email, [user_email])
            
            # Send the invoice email
            email.send()
            
        except ObjectDoesNotExist:
            pass
        
        # Empty the cart by setting session cart to empty dictionary
        request.session['cart'] = {}
        request.session.modified = True  # Mark session as changed
        
        # Render check out page, passing in items and total price
        return render(request, 'eCommerce/check_out.html', {
            'invoice': invoice_items,
            'total_price': total_price,
            })
    # Get all products from database
    products = Product.objects.all()
    # Show products list page, passing products to template and the error
    return render(request,
                    'eCommerce/products_list.html',
                    {'products': products,
                    'error': 'You do not have permission to buy products.'
                    }
                    )

# API to view vendors, stores and products
@api_view(['GET'])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def get_vendors_stores(request):
    """API endpoint returning every vendor along with their stores and products.

    :param request: HTTP request object (GET).
    :return: JsonResponse containing a list of serialized vendors.
    """
    if request.method == "GET":
        vendors = User.objects.filter(stores__isnull=False).distinct()
        serializer = VendorSerializer(vendors, many=True)
        return JsonResponse(data=serializer.data, safe=False)
    
# API for a vendor to add a store
@api_view(['POST'])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def post_store(request):
    """API endpoint allowing an authenticated vendor to create a new store for themselves.

    :param request: HTTP request object (POST); expects 'vendor', 'name' and 'description' fields.
    :return: Response with the created store data, or an error if validation/permission checks fail.
    """
    vendor_id = request.data.get('vendor')
    name = request.data.get('name')
    description = request.data.get('description')
    if vendor_id is None:
        return Response({'error': 'Vendor field is required.'}, status=status.HTTP_400_BAD_REQUEST)
    if name is None:
        return Response({'error': 'Name field is required.'}, status=status.HTTP_400_BAD_REQUEST)
    if description is None:
        return Response({'error': 'Description field is required.'}, status=status.HTTP_400_BAD_REQUEST)
    if int(vendor_id) != request.user.id:
        return Response({'error': 'User ID and vendor ID do not match.'}, status=status.HTTP_403_FORBIDDEN)
    # Check permissions
    user = request.user
    if user.has_perm('eCommerce.add_store') or user.has_perm('eCommerce.add_stores'):
        serializer = StorePostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return Response({'error': 'You do not have permission to add stores.'}, status=status.HTTP_403_FORBIDDEN)


# API for a vendor to add a product to a store
@api_view(['POST'])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def post_product(request):
    """API endpoint allowing an authenticated vendor to add a product to one of their own stores.

    :param request: HTTP request object (POST); expects 'store', 'name', 'description', 'price' and 'stock' fields.
    :return: Response with the created product data, or an error if validation/permission checks fail.
    """
    store = request.data.get('store')
    name = request.data.get('name')
    description = request.data.get('description')
    price = request.data.get('price')
    stock = request.data.get('stock')
    if store is None:
        return Response({'error': 'Store field is required.'}, status=status.HTTP_400_BAD_REQUEST)
    if name is None:
        return Response({'error': 'Name field is required.'}, status=status.HTTP_400_BAD_REQUEST)
    if description is None:
        return Response({'error': 'Description field is required.'}, status=status.HTTP_400_BAD_REQUEST)
    if price is None:
        return Response({'error': 'Price field is required.'}, status=status.HTTP_400_BAD_REQUEST)
    if stock is None:
        return Response({'error': 'Stock field is required.'}, status=status.HTTP_400_BAD_REQUEST)
    # Check that the user is trying to add a product to a store they created
    user = request.user
    user_stores = Store.objects.filter(vendor=user)
    for item in user_stores:
        if store == item.name:
            if user.has_perm('eCommerce.add_product') or user.has_perm('eCommerce.add_products'):
                # Bring the store object into the data and change data types
                data = request.data.copy()
                data['store'] = item.id
                data['price'] = float(data['price'])
                data['stock'] = int(data['stock'])
                serializer = ProductSerializer(data=data)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            return Response({'error': 'You do not have permission to add products.'}, status=status.HTTP_403_FORBIDDEN)
    return Response({'error': 'Store not found.'}, status=status.HTTP_400_BAD_REQUEST)


# API for a vendor to retrieve their reviews
@api_view(['GET'])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def get_vendors_reviews(request):
    """API endpoint returning the authenticated vendor's stores, products and reviews.

    :param request: HTTP request object (GET).
    :return: JsonResponse containing a list of the vendor's stores serialized with nested product reviews.
    """
    if request.method == "GET":
        vendor = request.user
        store_reviews = Store.objects.filter(vendor=vendor).distinct()
        serializer = StoreReviewSerializer(store_reviews, many=True)
        return JsonResponse(data=serializer.data, safe=False)
    
    
def external_posts(request):
    """Display posts fetched from the JSONPlaceholder API, optionally filtered by sample user ID.

    :param request: HTTP request object; accepts an optional 'user_id' GET parameter.
    :return: Rendered external_posts.html with the fetched posts and selected user ID.
    """
    user_id = request.GET.get("user_id")
    if user_id:
        try:
            user_id = int(user_id)
        except ValueError:
            user_id = None
    posts = get_posts()
    
    context = {
        "posts": posts,
        "selected_user_id": user_id
    }
    
    return render(
        request,
        "eCommerce/external_posts.html",
        context
        )
