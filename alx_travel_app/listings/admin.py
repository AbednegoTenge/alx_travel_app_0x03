from django.contrib import admin
from .models import Listing, Booking, Review


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ['title', 'host', 'city', 'country', 'property_type', 'price_per_night', 'is_available', 'created_at']
    list_filter = ['property_type', 'is_available', 'city', 'country', 'created_at']
    search_fields = ['title', 'description', 'city', 'country', 'address']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['host']


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['id', 'listing', 'guest', 'check_in', 'check_out', 'number_of_guests', 'total_price', 'status', 'created_at']
    list_filter = ['status', 'check_in', 'check_out', 'created_at']
    search_fields = ['listing__title', 'guest__username', 'guest__email']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['listing', 'guest']
    date_hierarchy = 'check_in'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['id', 'listing', 'user', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['listing__title', 'user__username', 'comment']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['listing', 'user', 'booking']
