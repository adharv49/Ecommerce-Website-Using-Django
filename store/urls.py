from django.urls import path
from . import views
from .views import custom_logout
from django.contrib.auth import views as auth_views 
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.home, name='home'),
   path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
 # urls.py
    path('accounts/register/', views.register, name='register'),
    path('accounts/profile/', views.profile, name='profile'),
    path('accounts/password_change/', auth_views.PasswordChangeView.as_view(template_name='registration/password_change_form.html'), name='password_change'),
    path('accounts/password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='registration/password_change_done.html'), name='password_change_done'),

   path('wishlist/', views.view_wishlist, name='wishlist'),
path('wishlist/add/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
path('search/', views.search, name='search'),
#path('wishlist/toggle/', views.toggle_wishlist2, name='toggle_wishlist2'),
path('wishlist/toggle/<int:product_id>/', views.toggle_wishlist_detail, name='toggle_wishlist_detail'),
#path('wishlist/toggle/', views.toggle_wishlist, name='toggle_wishlist'),
path('wishlist/remove/<int:product_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
path('review/add/<int:product_id>/', views.add_review, name='add_review'),
path('product/<int:product_id>/review/delete/', views.delete_review, name='delete_review'),
path('products/', views.product_list, name='product_list'),
path('product/<int:pk>/', views.product_details, name='product_details'),


 path('accounts/password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('accounts/password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('accounts/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('accounts/reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    
   path('checkout/remove/<int:item_id>/', views.remove_from_buy, name='remove_from_buy'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('checkout/add/<int:product_id>/', views.add_to_buy, name='add_to_buy'),
  
    path('accounts/logout/',custom_logout, name='logout'),
]
