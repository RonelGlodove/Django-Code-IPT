from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import login, logout
from .models import Product, Cart, Wishlist, Order, Feedback
from django import forms


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['name', 'email', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

def signup(r):
    if r.method == 'POST':
        form = UserCreationForm(r.POST)
        if form.is_valid():
            user = form.save()
            login(r, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(r, 'registration/signup.html', {'form': form})

def home(r):
    q=r.GET.get('q')
    p=Product.objects.all()
    if q: p=p.filter(name__icontains=q)
    return render(r,'store/home.html',{'p':p})

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
    items=Cart.objects.filter(user=r.user)
    total=sum(i.product.price for i in items)
    Order.objects.create(user=r.user,total=total)
    items.delete()
    return render(r,'store/checkout.html',{'total':total})

@login_required
def wishlist(r, id):
    Wishlist.objects.create(user=r.user, product_id=id)
    return redirect('home')

@login_required
def remove_from_cart(r, id):
    Cart.objects.filter(id=id, user=r.user).delete()


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
