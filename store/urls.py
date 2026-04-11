from django.urls import path
from . import views
urlpatterns = [
    path('', views.home, name='home'),
    path('home/', views.home, name='home_page'),
    path('products/', views.products, name='products'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('cart/', views.cart, name='cart'),
    path('wishlist/', views.wishlist_page, name='wishlist'),
    path('orders/', views.order_history, name='order_history'),
    path('add/<int:id>/', views.add_cart, name='add'),
    path('buy/<int:id>/', views.buy_now, name='buy_now'),
    path('remove/<int:id>/', views.remove_from_cart, name='remove_from_cart'),
    path('wishlist/remove/<int:id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('checkout/', views.checkout, name='checkout'),
    path('orders/<int:id>/cancel/', views.cancel_order, name='cancel_order'),
    path('orders/<int:id>/received/', views.mark_order_received, name='mark_order_received'),
    path('wish/<int:id>/', views.wishlist, name='wish'),
    path('signup/', views.signup, name='signup'),
    path('about/', views.about_us, name='about'),
    path('feedback/', views.feedback, name='feedback'),
    path('logout/', views.logout_view, name='logout'), 
]
