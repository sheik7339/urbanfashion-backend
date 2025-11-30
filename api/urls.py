from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import (
    CategoryViewSet, 
    ProductViewSet, 
    OrderViewSet, 
    ProfileViewSet, 
    UserViewSet, 
    CartItemViewSet, 
    RegisterView,
    RazorpayVerifyView,
    VerifyEmailView,
    ContactMessageViewSet,
    ReviewViewSet,
    WishlistViewSet
)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'profile', ProfileViewSet, basename='profile')
router.register(r'users', UserViewSet, basename='user')
router.register(r'cart', CartItemViewSet, basename='cart')
router.register(r'contact', ContactMessageViewSet, basename='contact')
router.register(r'reviews', ReviewViewSet, basename='review')
router.register(r'wishlist', WishlistViewSet, basename='wishlist')

urlpatterns = [
    path('', include(router.urls)),
    # JWT auth endpoints
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', RegisterView.as_view(), name='register'),
    path('verify-email/', VerifyEmailView.as_view(), name='verify-email'),
    path('razorpay/verify/', RazorpayVerifyView.as_view(), name='razorpay-verify'),
]
