from django.contrib import admin
from .models import Category, Product, Order, OrderItem, Profile, CartItem, ContactMessage, Review, Wishlist

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'price', 'stock_quantity', 'is_featured']
    list_filter = ['category', 'is_featured']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ['stock_quantity', 'is_featured']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'status', 'total_amount', 'payment_verified', 'created_at']
    list_filter = ['status', 'payment_verified', 'created_at']
    search_fields = ['user__email', 'user__username', 'shipping_name']
    readonly_fields = ['created_at', 'total_amount']
    list_editable = ['status', 'payment_verified']
    fieldsets = (
        ('Order Info', {
            'fields': ('user', 'status', 'total_amount', 'created_at')
        }),
        ('Shipping Details', {
            'fields': ('shipping_name', 'shipping_phone', 'shipping_address', 'shipping_city', 'shipping_state', 'shipping_pincode')
        }),
        ('Payment Details', {
            'fields': ('payment_method', 'payment_screenshot', 'payment_verified')
        }),
    )

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'size', 'quantity', 'price']
    list_filter = ['size']

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'is_verified']
    list_filter = ['is_verified']
    search_fields = ['user__email', 'user__username', 'phone']

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'size', 'quantity', 'added_at']
    list_filter = ['size', 'added_at']
    search_fields = ['user__email', 'product__title']

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'created_at', 'is_read']
    list_filter = ['is_read', 'created_at']
    search_fields = ['name', 'email', 'message']
    readonly_fields = ['created_at']
    list_editable = ['is_read']
    
    def has_add_permission(self, request):
        # Prevent adding messages from admin (they should come from frontend)
        return False

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'verified_purchase', 'created_at']
    list_filter = ['rating', 'verified_purchase', 'created_at']
    search_fields = ['product__title', 'user__username', 'comment']
    readonly_fields = ['created_at']
    list_editable = ['verified_purchase']

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'added_at']
    list_filter = ['added_at']
    search_fields = ['user__username', 'product__title']
    readonly_fields = ['added_at']

