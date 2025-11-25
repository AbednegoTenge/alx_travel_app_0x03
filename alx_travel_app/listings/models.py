from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User


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
        related_name='listings',
        help_text='The user who owns/hosts this listing'
    )
    title = models.CharField(max_length=200, help_text='Title of the listing')
    description = models.TextField(help_text='Detailed description of the listing')
    address = models.CharField(max_length=255, help_text='Street address')
    city = models.CharField(max_length=100, help_text='City name')
    country = models.CharField(max_length=100, help_text='Country name')
    property_type = models.CharField(
        max_length=20,
        choices=PROPERTY_TYPES,
        help_text='Type of property'
    )
    price_per_night = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text='Price per night in local currency'
    )
    max_guests = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text='Maximum number of guests allowed'
    )
    bedrooms = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(0)],
        help_text='Number of bedrooms'
    )
    bathrooms = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(0)],
        help_text='Number of bathrooms'
    )
    amenities = models.JSONField(
        default=list,
        blank=True,
        help_text='List of amenities (e.g., ["WiFi", "Pool", "Parking"])'
    )
    is_available = models.BooleanField(
        default=True,
        help_text='Whether the listing is currently available for booking'
    )
    created_at = models.DateTimeField(auto_now_add=True, help_text='Creation timestamp')
    updated_at = models.DateTimeField(auto_now=True, help_text='Last update timestamp')
    
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
    """Model representing a booking/reservation for a listing."""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]
    
    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name='bookings',
        help_text='The listing being booked'
    )
    guest = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='bookings',
        help_text='The user making the booking'
    )
    check_in = models.DateField(help_text='Check-in date')
    check_out = models.DateField(help_text='Check-out date')
    number_of_guests = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text='Number of guests for this booking'
    )
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text='Total price for the booking'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text='Current status of the booking'
    )
    special_requests = models.TextField(
        blank=True,
        null=True,
        help_text='Any special requests from the guest'
    )
    created_at = models.DateTimeField(auto_now_add=True, help_text='Booking creation timestamp')
    updated_at = models.DateTimeField(auto_now=True, help_text='Last update timestamp')
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['listing', 'check_in', 'check_out']),
            models.Index(fields=['guest']),
            models.Index(fields=['status']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(check_out__gt=models.F('check_in')),
                name='check_out_after_check_in'
            ),
        ]
    
    def __str__(self):
        return f"Booking #{self.id} - {self.listing.title} by {self.guest.username}"
    
    def clean(self):
        from django.core.exceptions import ValidationError
        if self.check_out <= self.check_in:
            raise ValidationError('Check-out date must be after check-in date.')
        if self.number_of_guests > self.listing.max_guests:
            raise ValidationError(
                f'Number of guests ({self.number_of_guests}) exceeds maximum '
                f'guests allowed ({self.listing.max_guests}) for this listing.'
            )


class Review(models.Model):
    """Model representing a review/rating for a listing."""
    
    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name='reviews',
        help_text='The listing being reviewed'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        help_text='The user writing the review'
    )
    booking = models.ForeignKey(
        Booking,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='review',
        help_text='The booking associated with this review (optional)'
    )
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text='Rating from 1 to 5 stars'
    )
    comment = models.TextField(
        blank=True,
        null=True,
        help_text='Review comment/text'
    )
    created_at = models.DateTimeField(auto_now_add=True, help_text='Review creation timestamp')
    updated_at = models.DateTimeField(auto_now=True, help_text='Last update timestamp')
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['listing', 'rating']),
            models.Index(fields=['user']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['listing', 'user'],
                name='unique_user_listing_review',
            ),
        ]
    
    def __str__(self):
        return f"Review by {self.user.username} for {self.listing.title} - {self.rating} stars"