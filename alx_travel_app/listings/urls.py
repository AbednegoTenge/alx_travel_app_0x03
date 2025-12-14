from rest_framework.routers import DefaultRouter
from .views import ListingViewSet, BookingViewSet, PaymentViewSet, UserViewSet


router = DefaultRouter()
router.register(r'listings', ListingViewSet, basename='listing')
router.register(r'bookings', BookingViewSet, basename='booking')
router.register(r'payments', PaymentViewSet, basename='payment')
router.register(r'users', UserViewSet, basename='user')

urlpatterns = router.urls

