from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group, User
from django.utils.html import format_html
from django.utils import timezone
from .models import Product, Cart, Wishlist, Order, OrderItem, Feedback, UserProfile


admin.site.unregister(Group)
admin.site.unregister(User)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'is_staff', 'is_superuser', 'is_active']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    readonly_fields = ['last_login', 'date_joined']

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Access', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_staff', 'is_superuser', 'is_active'),
        }),
    )


def image_preview(image_field, size=60, rounded=False):
    if image_field:
        radius = '50%' if rounded else '14px'
        return format_html(
            '<img src="{}" alt="Preview" style="width: {}px; height: {}px; object-fit: cover; border-radius: {}; box-shadow: 0 6px 18px rgba(0,0,0,0.12);" />',
            image_field.url,
            size,
            size,
            radius,
        )
    return 'No image'

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'profile_preview', 'phone', 'place', 'age', 'birthday', 'city', 'country', 'created_at']
    search_fields = ['user__username', 'user__email', 'phone', 'place', 'city', 'country']
    list_filter = ['country', 'city', 'created_at']
    readonly_fields = ['profile_preview', 'profile_file_link', 'created_at', 'updated_at']

    fieldsets = (
        ('User', {
            'fields': ('user',),
        }),
        ('Profile Details', {
            'fields': ('profile_preview', 'profile_file_link', 'profile_picture', 'phone', 'place', 'age', 'birthday', 'address', 'city', 'postal_code', 'country'),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
        }),
    )

    def profile_preview(self, obj):
        return image_preview(obj.profile_picture, rounded=True)
    profile_preview.short_description = 'Picture'

    def profile_file_link(self, obj):
        if obj.profile_picture:
            return format_html('<a href="{}" target="_blank">Open uploaded file</a>', obj.profile_picture.url)
        return 'No file'
    profile_file_link.short_description = 'Uploaded File'

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['product_preview', 'name', 'price']
    search_fields = ['name']
    list_filter = ['price']
    readonly_fields = ['product_preview']

    def product_preview(self, obj):
        return image_preview(obj.image, size=72)
    product_preview.short_description = 'Picture'

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'product_preview', 'product']
    search_fields = ['user__username', 'product__name']
    list_filter = ['user']

    def product_preview(self, obj):
        return image_preview(obj.product.image)
    product_preview.short_description = 'Picture'

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'product_preview', 'product']
    search_fields = ['user__username', 'product__name']
    list_filter = ['user']

    def product_preview(self, obj):
        return image_preview(obj.product.image)
    product_preview.short_description = 'Picture'


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product_preview', 'product', 'product_name', 'product_price']
    can_delete = False

    def product_preview(self, obj):
        return image_preview(obj.product.image)
    product_preview.short_description = 'Picture'


@admin.action(description='Mark selected orders as waiting')
def mark_orders_waiting(modeladmin, request, queryset):
    queryset.update(status=Order.STATUS_WAITING, updated_at=timezone.now())


@admin.action(description='Mark selected orders as successful')
def mark_orders_successful(modeladmin, request, queryset):
    queryset.update(status=Order.STATUS_SUCCESSFUL, updated_at=timezone.now())


@admin.action(description='Mark selected orders as received')
def mark_orders_received(modeladmin, request, queryset):
    queryset.update(status=Order.STATUS_RECEIVED, updated_at=timezone.now())


@admin.action(description='Mark selected orders as cancelled')
def mark_orders_cancelled(modeladmin, request, queryset):
    queryset.update(status=Order.STATUS_CANCELLED, updated_at=timezone.now())


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'status_badge', 'ordered_products', 'user_profile_preview', 'user_email', 'user_phone', 'user_place', 'user_location', 'total', 'created_at']
    search_fields = ['user__username', 'user__email', 'user__profile__phone', 'user__profile__place', 'user__profile__city', 'user__profile__country', 'items__product_name']
    list_filter = ['status', 'user', 'user__profile__country', 'user__profile__city', 'created_at']
    readonly_fields = ['user', 'total', 'created_at', 'updated_at', 'user_profile_preview', 'user_profile_file', 'user_email', 'user_phone', 'user_place', 'user_age', 'user_birthday', 'user_address', 'user_location']
    list_select_related = ['user', 'user__profile']
    inlines = [OrderItemInline]
    actions = [mark_orders_waiting, mark_orders_successful, mark_orders_received, mark_orders_cancelled]

    fieldsets = (
        ('Order', {
            'fields': ('user', 'status', 'total', 'created_at', 'updated_at'),
        }),
        ('Customer Profile', {
            'fields': ('user_profile_preview', 'user_profile_file', 'user_email', 'user_phone', 'user_place', 'user_age', 'user_birthday', 'user_address', 'user_location'),
        }),
    )

    def user_profile_preview(self, obj):
        return image_preview(obj.user.profile.profile_picture, size=70, rounded=True)
    user_profile_preview.short_description = 'Picture'

    def user_profile_file(self, obj):
        if obj.user.profile.profile_picture:
            return format_html('<a href="{}" target="_blank">Open uploaded file</a>', obj.user.profile.profile_picture.url)
        return 'No file'
    user_profile_file.short_description = 'Uploaded File'

    def user_email(self, obj):
        return obj.user.email or 'No email'
    user_email.short_description = 'Email'

    def user_phone(self, obj):
        return obj.user.profile.phone or 'No phone'
    user_phone.short_description = 'Phone'

    def user_place(self, obj):
        return obj.user.profile.place or 'No place'
    user_place.short_description = 'Place'

    def user_age(self, obj):
        return obj.user.profile.age or 'No age'
    user_age.short_description = 'Age'

    def user_birthday(self, obj):
        return obj.user.profile.birthday or 'No birthday'
    user_birthday.short_description = 'Birthday'

    def user_address(self, obj):
        return obj.user.profile.address or 'No address'
    user_address.short_description = 'Address'

    def user_location(self, obj):
        profile = obj.user.profile
        parts = [profile.city, profile.country]
        return ', '.join(part for part in parts if part) or 'No location'
    user_location.short_description = 'Location'

    def ordered_products(self, obj):
        names = list(obj.items.values_list('product_name', flat=True))
        return ', '.join(names[:3]) + ('...' if len(names) > 3 else '') if names else 'No items'
    ordered_products.short_description = 'Ordered Items'

    def status_badge(self, obj):
        colors = {
            Order.STATUS_WAITING: '#f0ad4e',
            Order.STATUS_SUCCESSFUL: '#198754',
            Order.STATUS_RECEIVED: '#0d6efd',
            Order.STATUS_CANCELLED: '#dc3545',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="display:inline-block;padding:4px 10px;border-radius:999px;background:{};color:#fff;font-weight:600;">{}</span>',
            color,
            obj.get_status_display(),
        )
    status_badge.short_description = 'Status'

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'created_at']
    search_fields = ['name', 'email']
    list_filter = ['created_at']
    readonly_fields = ['created_at']
