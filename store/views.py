from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import FeedbackForm, SignUpForm, UserAccountForm, UserProfileForm
from .models import Cart, Order, OrderItem, Product, Wishlist


def missing_profile_fields(user):
    profile = user.profile
    required_fields = {
        'email': user.email,
        'phone': profile.phone,
        'place': profile.place,
        'age': profile.age,
        'birthday': profile.birthday,
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
    q=r.GET.get('q')
    p=Product.objects.all()
    if q: p=p.filter(name__icontains=q)
    return render(r,'store/home.html',{'p':p})

def products(r):
    q = r.GET.get('q')
    p = Product.objects.all()
    if q:
        p = p.filter(name__icontains=q)
    return render(r, 'store/products.html', {'p': p})

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
def checkout(r):
    missing_fields = missing_profile_fields(r.user)
    if missing_fields:
        messages.warning(
            r,
            'Please complete your profile before checkout. Missing: ' + ', '.join(missing_fields) + '.'
        )
        return redirect('edit_profile')

    items=Cart.objects.filter(user=r.user)
    if not items.exists():
        messages.warning(r, 'Your cart is empty.')
        return redirect('cart')

    total=sum(i.product.price for i in items)
    order = Order.objects.create(user=r.user,total=total)
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
    return render(r,'store/checkout.html',{'total':total, 'order': order})


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
    Wishlist.objects.create(user=r.user, product_id=id)
    return redirect('home')

@login_required
def remove_from_cart(r, id):
    Cart.objects.filter(id=id, user=r.user).delete()


@login_required
def profile(r):
    return render(r, 'store/profile.html', {'profile': r.user.profile})

@login_required
def edit_profile(r):
    profile = r.user.profile
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
    return redirect('home_page')
