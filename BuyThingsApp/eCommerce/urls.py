from django.urls import path
from . import views

app_name = 'eCommerce'  # This helps Django know these URLs belong to the eCommerce app

urlpatterns = [
    # Home page: Shows the list of all products
    path('', views.list_products, name='products_list'),

    # Page to view details about a specific product (with a search form)
    path('product/', views.view_product_page, name='product_page'),
    
    # Page to view the stores of the logged in vendor
    path('stores/', views.store_list, name='store_list'),

    # URL to add an item to the shopping cart (usually called by a form)
    path('add-to-cart/', views.add_item_to_cart, name='add_to_cart'),

    # Page showing all items currently in the user's cart with totals
    path('cart/', views.show_user_cart, name='main_cart_page'),

    # URL to clear all items from the user's cart
    path('clear-cart/', views.clear_cart, name='clear_cart'),
    
    # Pge showing the invoice that is also used to send the invoice to the user email and clear the cart
    path('check-out/', views.check_out, name='check_out'),
    
    # URL pattern for displaying details of a specific product
    path("product/<int:pk>/", views.product_detail, name="product_detail"),
    
    # URL pattern for creating a new product
    path("store/<int:pk>/product/new/", views.product_create, name="product_create"),
    
    # URL pattern for updating an existing product
    path("product/<int:pk>/edit/", views.product_update, name="product_update"),
    
    # URL pattern for deleting an existing product
    path("product/<int:pk>/delete/", views.product_delete, name="product_delete"),
    
    # URL pattern for displaying details of a specific store
    path("store/<int:pk>/", views.store_detail, name="store_detail"),
    
    # URL pattern for creating a new store
    path("store/new/", views.store_create, name="store_create"),
    
    # URL pattern for updating an existing store
    path("store/<int:pk>/edit/", views.store_update, name="store_update"),
    
    # URL pattern for deleting an existing store
    path("store/<int:pk>/delete/", views.store_delete, name="store_delete"),
    
    # URL pattern for displaying details of a specific review
    path("product/review/<int:pk>/", views.review_detail, name="review_detail"),
    
    # URL pattern for creating a new review
    path("product/<int:pk>/review/new/", views.review_create, name="review_create"),
    
    # URL pattern for updating an existing review
    path("product/review/<int:pk>/edit/", views.review_update, name="review_update"),
    
    # URL pattern for deleting an existing review
    path("product/review/<int:pk>/delete/", views.review_delete, name="review_delete"),
    
    # URL path for an API request to get a list of vendors, stores and products
    path('api/vendors/', views.get_vendors_stores, name="get_vendors_stores"),
    
    # URL path for an API request to get a list of reviews for a logged-in vendor
    path('api/reviews/', views.get_vendors_reviews, name="get_vendors_reviews"),
    
    # URL path for an API request to add a store
    path('api/post/store/', views.post_store, name="post_store"),
    
    # URL path for an API request to add a product
    path('api/post/product/', views.post_product, name="post_product"),
    
    # URL path to view posts through an API
    path( "external-posts/", views.external_posts, name="external_posts" ),
    
]
