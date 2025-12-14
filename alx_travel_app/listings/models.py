from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import AbstractUser
from django.db.models import Q, F
from django.conf import settings


class User(AbstractUser):
    ROLE_GUEST = 'guest'
    ROLE_HOST = 'host'
    ROLE_CHOICES = [
        (ROLE_GUEST, 'Guest'),
        (ROLE_HOST, 'Host'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=ROLE_GUEST)

    @property
    def is_host(self):
        return self.role == self.ROLE_HOST

    @property
    def is_guest(self):
        return self.role == self.ROLE_GUEST

class Listing(models.Model):
    """Model representing a travel accommodation listing."""

    PROPERTY_TYPES = [
        ('apartment', 'Apartment'),
        ('house', 'House'),
        ('hotel', 'Hotel'),
        ('villa', 'Villa'),
        ('cottage', 'Cottage'),
        ('hostel', 'Hostel'),
        ('resort', 'Resort'),
    ]

    host = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='listings'
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    property_type = models.CharField(
        max_length=20,
        choices=PROPERTY_TYPES
    )
    price_per_night = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    max_guests = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )
    bedrooms = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(0)]
    )
    bathrooms = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(0)]
    )
    amenities = models.JSONField(default=list, blank=True)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['city', 'country']),
            models.Index(fields=['property_type']),
            models.Index(fields=['price_per_night']),
            models.Index(fields=['is_available']),
        ]

    def __str__(self):
        return f"{self.title} - {self.city}, {self.country}"


class Booking(models.Model):
    """Model representing a booking for a listing."""

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]

    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name='bookings'
    )
    guest = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='bookings'
    )
    check_in = models.DateField()
    check_out = models.DateField()
    number_of_guests = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    special_requests = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['listing', 'check_in', 'check_out']),
            models.Index(fields=['guest']),
            models.Index(fields=['status']),
        ]
        constraints = [
            models.CheckConstraint(
                condition=Q(check_out__gt=F('check_in')),
                name='check_out_after_check_in'
            ),
        ]

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.check_out <= self.check_in:
            raise ValidationError('Check-out date must be after check-in date.')

        if self.number_of_guests > self.listing.max_guests:
            raise ValidationError(
                f'Number of guests ({self.number_of_guests}) exceeds '
                f'maximum allowed ({self.listing.max_guests}).'
            )

    def __str__(self):
        return f"Booking #{self.id} - {self.listing.title}"


class Review(models.Model):
    """Model representing a review for a listing."""

    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    booking = models.ForeignKey(
        Booking,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='review'
    )
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['listing', 'rating']),
            models.Index(fields=['user']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['listing', 'user'],
                name='unique_user_listing_review'
            ),
        ]

    def __str__(self):
        return f"Review by {self.user.username} - {self.rating}★"


class Payment(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('chapa', 'Chapa'),
        ('telebirr', 'Telebirr'),
        ('mpesa', 'M-Pesa'),
        ('ebirr', 'eBirr'),
    ]

    booking = models.OneToOneField(
        Booking,
        on_delete=models.CASCADE,
        related_name='payment'
    )
    transaction_id = models.CharField(
        max_length=255,
        unique=True,
        null=True,
        blank=True
    )
    chapa_reference = models.CharField(max_length=255, unique=True)
    checkout_url = models.URLField(null=True, blank=True)

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='GHC')
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default='chapa'
    )
    status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='pending'
    )

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20, null=True, blank=True)

    payment_initiated_at = models.DateTimeField(auto_now_add=True)
    payment_completed_at = models.DateTimeField(null=True, blank=True)
    failure_reason = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['transaction_id']),
            models.Index(fields=['chapa_reference']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"Payment {self.chapa_reference} - {self.status}"
