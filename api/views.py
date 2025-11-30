from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth import get_user_model
from django.conf import settings
from django.db import models
from .models import Category, Product, Order, OrderItem, Profile, CartItem, ContactMessage, Review, Wishlist
from .serializers import (
    CategorySerializer,
    ProductSerializer,
    OrderSerializer,
    OrderItemSerializer,
    ProfileSerializer,
    UserSerializer,
    CartItemSerializer,
    RegisterSerializer,
    ContactMessageSerializer,
    ReviewSerializer,
    WishlistSerializer,
)
import razorpay
import uuid
from django.core.mail import send_mail
from django.conf import settings

User = get_user_model()

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]

class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.select_related('category').prefetch_related('reviews').all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Search functionality
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                models.Q(title__icontains=search) |
                models.Q(description__icontains=search) |
                models.Q(category__name__icontains=search)
            )
        
        # Filter by category
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category__slug=category)
        
        # Filter by stock
        in_stock = self.request.query_params.get('in_stock', None)
        if in_stock == 'true':
            queryset = queryset.filter(stock_quantity__gt=0)
        
        return queryset

    @action(detail=False, methods=['get'], url_path='featured')
    def featured(self, request):
        featured = self.get_queryset().filter(is_featured=True, stock_quantity__gt=0)[:6]
        serializer = self.get_serializer(featured, many=True)
        return Response(serializer.data)


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.select_related('user').prefetch_related('items__product').all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        if self.request.user.is_staff:
            return super().get_queryset()
        return super().get_queryset().filter(user=self.request.user)

# ----- Cart endpoints -----
class CartItemViewSet(viewsets.ModelViewSet):
    """Cart items for the authenticated user. Supports list, create, update (PATCH), and delete."""
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save()

# ----- User registration -----
class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate verification token
        token = str(uuid.uuid4())
        profile, created = Profile.objects.get_or_create(user=user)
        profile.verification_token = token
        profile.save()
        
        # Send verification email
        verification_link = f"http://localhost:5173/verify-email?token={token}"
        send_mail(
            "Verify your UrbanFashion account",
            f"Click here to verify your account: {verification_link}",
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=True,
        )
        
        return Response({"id": user.id, "username": user.username, "email": user.email}, status=status.HTTP_201_CREATED)

class VerifyEmailView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        token = request.query_params.get('token')
        if not token:
            return Response({'error': 'Token required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            profile = Profile.objects.get(verification_token=token)
            if profile.is_verified:
                return Response({'message': 'Already verified'}, status=status.HTTP_200_OK)
            
            profile.is_verified = True
            profile.verification_token = '' # Clear token
            profile.save()
            return Response({'message': 'Email verified successfully'}, status=status.HTTP_200_OK)
        except Profile.DoesNotExist:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)

# ----- Razorpay Verification -----
class RazorpayVerifyView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        data = request.data
        try:
            # Initialize Razorpay client
            # Ensure RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET are in settings.py
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            
            # Verify signature
            params_dict = {
                'razorpay_order_id': data.get('razorpay_order_id'),
                'razorpay_payment_id': data.get('razorpay_payment_id'),
                'razorpay_signature': data.get('razorpay_signature')
            }
            
            # This will raise an error if verification fails
            client.utility.verify_payment_signature(params_dict)
            
            # Update order status
            order_id = data.get('order_id')
            if order_id:
                order = Order.objects.get(id=order_id, user=request.user)
                order.status = 'processing' # Mark as paid/processing
                order.save()
                return Response({'status': 'Payment verified'}, status=status.HTTP_200_OK)
            else:
                 return Response({'error': 'Order ID missing'}, status=status.HTTP_400_BAD_REQUEST)

        except razorpay.errors.SignatureVerificationError:
            return Response({'error': 'Signature verification failed'}, status=status.HTTP_400_BAD_REQUEST)
        except Order.DoesNotExist:
             return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ProfileViewSet(viewsets.GenericViewSet, viewsets.mixins.RetrieveModelMixin, viewsets.mixins.UpdateModelMixin):
    queryset = Profile.objects.select_related('user').all()
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user.profile

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return super().get_queryset()
        return User.objects.filter(id=self.request.user.id)

class ContactMessageViewSet(viewsets.ModelViewSet):
    """Contact form submissions. Anyone can create, only admins can view all."""
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer
    permission_classes = [permissions.AllowAny]  # Allow anyone to submit
    http_method_names = ['post', 'get', 'patch']  # Only allow POST for public, GET/PATCH for admin

    def get_queryset(self):
        # Only admins can view all messages
        if self.request.user.is_staff:
            return super().get_queryset()
        # Non-admins can't list messages
        return ContactMessage.objects.none()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        # Optionally send email notification to admin
        try:
            send_mail(
                f"New Contact Message from {serializer.validated_data['name']}",
                f"Name: {serializer.validated_data['name']}\nEmail: {serializer.validated_data['email']}\n\nMessage:\n{serializer.validated_data['message']}",
                settings.DEFAULT_FROM_EMAIL,
                [settings.DEFAULT_FROM_EMAIL],  # Send to yourself
                fail_silently=True,
            )
        except Exception as e:
            print(f"Failed to send email notification: {e}")
        
        return Response(
            {"message": "Your message has been sent successfully. We'll get back to you soon!"},
            status=status.HTTP_201_CREATED
        )

class ReviewViewSet(viewsets.ModelViewSet):
    """Product reviews. Users can create, view, update, and delete their own reviews."""
    queryset = Review.objects.select_related('user', 'product').all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        # Filter by product if specified
        product_id = self.request.query_params.get('product', None)
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        # Only allow users to update their own reviews
        if serializer.instance.user != self.request.user:
            raise permissions.PermissionDenied("You can only edit your own reviews")
        serializer.save()

    def perform_destroy(self, instance):
        # Only allow users to delete their own reviews
        if instance.user != self.request.user:
            raise permissions.PermissionDenied("You can only delete your own reviews")
        instance.delete()

class WishlistViewSet(viewsets.ModelViewSet):
    """User wishlist. Users can add/remove products from their wishlist."""
    queryset = Wishlist.objects.select_related('user', 'product').all()
    serializer_class = WishlistSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Users can only see their own wishlist
        return super().get_queryset().filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
