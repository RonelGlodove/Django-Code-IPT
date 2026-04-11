from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import FeedbackForm, SignUpForm, UserAccountForm, UserProfileForm
from .models import Cart, Order, OrderItem, Product, UserProfile, Wishlist


def get_product_results(query):
    products = Product.objects.all()
    cleaned_query = (query or '').strip()

    if not cleaned_query:
        return products, ''

    for term in cleaned_query.split():
        term_filter = Q(name__icontains=term)
        try:
            term_filter |= Q(price=float(term))
        except ValueError:
            pass
        products = products.filter(term_filter)

    return products, cleaned_query


def missing_profile_fields(user):
    profile, _ = UserProfile.objects.get_or_create(user=user)
    required_fields = {
        'email': user.email,
        'phone number': profile.phone,
        'address': profile.address,
        'city': profile.city,
        'zip code': profile.postal_code,
        'place': profile.place,
    }
    return [label for label, value in required_fields.items() if not value]

def signup(r):
    if r.method == 'POST':
        form = SignUpForm(r.POST)
        if form.is_valid():
            user = form.save()
            login(r, user)
            return redirect('home')
    else:
        form = SignUpForm()
    return render(r, 'registration/signup.html', {'form': form})

def home(r):
    p, q = get_product_results(r.GET.get('q'))
    return render(r, 'store/home.html', {'p': p, 'q': q})

def products(r):
    p, q = get_product_results(r.GET.get('q'))
    return render(r, 'store/products.html', {'p': p, 'q': q})

@login_required
def add_cart(r,id):
    Cart.objects.create(user=r.user,product_id=id)
    return redirect('cart')

@login_required
def cart(r):
    items=Cart.objects.filter(user=r.user)
    total=sum(i.product.price for i in items)
    return render(r,'store/cart.html',{'items':items,'total':total})

@login_required
def buy_now(r, id):
    # Create cart item and immediately set it as the only item for checkout
    item = Cart.objects.create(user=r.user, product_id=id)
    r.session['checkout_item_ids'] = [str(item.id)]
    return redirect('checkout')


@login_required
def checkout(r):
    missing_fields = missing_profile_fields(r.user)
    if missing_fields:
        messages.warning(
            r,
            'Please complete your profile before checkout. Missing: ' + ', '.join(missing_fields) + '.'
        )
        return redirect('edit_profile')

    # Handle selection from cart page (POST) or session persistence
    if r.method == 'POST' and 'selected_items' in r.POST:
        r.session['checkout_item_ids'] = r.POST.getlist('selected_items')

    selected_ids = r.session.get('checkout_item_ids')
    if selected_ids:
        items = Cart.objects.filter(user=r.user, id__in=selected_ids)
    else:
        items = Cart.objects.filter(user=r.user)

    if not items.exists():
        messages.warning(r, 'No items selected for checkout.')
        return redirect('cart')

    total = sum(i.product.price for i in items)

    if r.method == 'POST':
        payment_method = r.POST.get('payment_method')
        if not payment_method:
            messages.error(r, 'Please select a payment method.')
        else:
            # Process order after user confirms details and selects payment
            order = Order.objects.create(user=r.user, total=total, payment_method=payment_method)
            OrderItem.objects.bulk_create([
                OrderItem(
                    order=order,
                    product=item.product,
                    product_name=item.product.name,
                    product_price=item.product.price,
                )
                for item in items
            ])
            items.delete()
            if 'checkout_item_ids' in r.session:
                del r.session['checkout_item_ids']
            messages.success(r, f'Order placed successfully via {payment_method}!')
            return render(r, 'store/checkout.html', {
                'total': total,
                'order': order,
                'payment_method': payment_method,
                'success': True
            })

    # GET request: Display confirmation page with profile details and payment options
    payment_methods = ['PayMaya', 'GCash', 'Credit Card', 'Cash on Delivery']
    profile, _ = UserProfile.objects.get_or_create(user=r.user)
    return render(r, 'store/checkout.html', {'items': items, 'total': total, 'profile': profile, 'payment_methods': payment_methods})


@login_required
def order_history(r):
    orders = (
        Order.objects.filter(user=r.user)
        .prefetch_related('items', 'items__product')
        .order_by('-created_at', '-id')
    )
    return render(r, 'store/order_history.html', {'orders': orders})


@login_required
def cancel_order(r, id):
    order = get_object_or_404(Order, id=id, user=r.user)
    if r.method != 'POST':
        return redirect('order_history')

    if order.status != Order.STATUS_WAITING:
        messages.warning(r, 'Only waiting orders can be cancelled.')
        return redirect('order_history')

    order.status = Order.STATUS_CANCELLED
    order.save(update_fields=['status', 'updated_at'])
    messages.success(r, 'Your order has been cancelled.')
    return redirect('order_history')


@login_required
def mark_order_received(r, id):
    order = get_object_or_404(Order, id=id, user=r.user)
    if r.method != 'POST':
        return redirect('order_history')

    if order.status != Order.STATUS_SUCCESSFUL:
        messages.warning(r, 'Only successful orders can be marked as received.')
        return redirect('order_history')

    order.status = Order.STATUS_RECEIVED
    order.save(update_fields=['status', 'updated_at'])
    messages.success(r, 'Order marked as received.')
    return redirect('order_history')

@login_required
def wishlist(r, id):
    wishlist_item, created = Wishlist.objects.get_or_create(user=r.user, product_id=id)
    if created:
        messages.success(r, f'"{wishlist_item.product.name}" was added to your wishlist.')
    else:
        messages.info(r, f'"{wishlist_item.product.name}" is already in your wishlist.')
    return redirect('wishlist')


@login_required
def wishlist_page(r):
    items = Wishlist.objects.filter(user=r.user).select_related('product')
    return render(r, 'store/wishlist.html', {'items': items})


@login_required
def remove_from_wishlist(r, id):
    Wishlist.objects.filter(id=id, user=r.user).delete()
    messages.success(r, 'Item removed from your wishlist.')
    return redirect('wishlist')

@login_required
def remove_from_cart(r, id):
    Cart.objects.filter(id=id, user=r.user).delete()
    messages.success(r, 'Item removed from your cart.')
    return redirect('cart')


@login_required
def profile(r):
    profile, _ = UserProfile.objects.get_or_create(user=r.user)
    return render(r, 'store/profile.html', {'profile': profile})

@login_required
def edit_profile(r):
    profile, _ = UserProfile.objects.get_or_create(user=r.user)
    if r.method == 'POST':
        form = UserProfileForm(r.POST, r.FILES, instance=profile)
        user_form = UserAccountForm(r.POST, instance=r.user)
        if form.is_valid() and user_form.is_valid():
            user_form.save()
            form.save()
            messages.success(r, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=profile)
        user_form = UserAccountForm(instance=r.user)
    return render(r, 'store/edit_profile.html', {'form': form, 'user_form': user_form, 'profile': profile})


def about_us(r):
    return render(r, 'store/about.html')


def feedback(r):
    if r.method == 'POST':
        form = FeedbackForm(r.POST)
        if form.is_valid():
            feedback_obj = form.save(commit=False)
            if r.user.is_authenticated:
                feedback_obj.user = r.user
            feedback_obj.save()
            messages.success(r, 'Thank you for your feedback! We appreciate your input.')
            return redirect('home')
    else:
        form = FeedbackForm()
    return render(r, 'store/feedback.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')
