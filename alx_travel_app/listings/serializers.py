from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Listing, Booking


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model (used in nested relationships)."""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']


class ListingSerializer(serializers.ModelSerializer):
    """Serializer for Listing model."""
    
    host = UserSerializer(read_only=True)
    host_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='host',
        write_only=True,
        required=True
    )
    property_type_display = serializers.CharField(
        source='get_property_type_display',
        read_only=True
    )
    
    class Meta:
        model = Listing
        fields = [
            'id',
            'host',
            'host_id',
            'title',
            'description',
            'address',
            'city',
            'country',
            'property_type',
            'property_type_display',
            'price_per_night',
            'max_guests',
            'bedrooms',
            'bathrooms',
            'amenities',
            'is_available',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_price_per_night(self, value):
        """Validate that price per night is non-negative."""
        if value < 0:
            raise serializers.ValidationError("Price per night must be non-negative.")
        return value
    
    def validate_max_guests(self, value):
        """Validate that max guests is at least 1."""
        if value < 1:
            raise serializers.ValidationError("Maximum guests must be at least 1.")
        return value


class ListingListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing list views."""
    
    host_username = serializers.CharField(source='host.username', read_only=True)
    property_type_display = serializers.CharField(
        source='get_property_type_display',
        read_only=True
    )
    
    class Meta:
        model = Listing
        fields = [
            'id',
            'title',
            'city',
            'country',
            'property_type',
            'property_type_display',
            'price_per_night',
            'max_guests',
            'bedrooms',
            'bathrooms',
            'is_available',
            'host_username',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class BookingSerializer(serializers.ModelSerializer):
    """Serializer for Booking model."""
    
    listing = ListingListSerializer(read_only=True)
    listing_id = serializers.PrimaryKeyRelatedField(
        queryset=Listing.objects.all(),
        source='listing',
        write_only=True,
        required=True
    )
    guest = UserSerializer(read_only=True)
    guest_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='guest',
        write_only=True,
        required=True
    )
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )
    number_of_nights = serializers.SerializerMethodField()
    
    class Meta:
        model = Booking
        fields = [
            'id',
            'listing',
            'listing_id',
            'guest',
            'guest_id',
            'check_in',
            'check_out',
            'number_of_guests',
            'total_price',
            'status',
            'status_display',
            'special_requests',
            'number_of_nights',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_number_of_nights(self, obj):
        """Calculate the number of nights for the booking."""
        if obj.check_in and obj.check_out:
            return (obj.check_out - obj.check_in).days
        return None
    
    def validate(self, data):
        """Validate booking data."""
        check_in = data.get('check_in')
        check_out = data.get('check_out')
        listing = data.get('listing')
        number_of_guests = data.get('number_of_guests')
        
        # Validate check-out is after check-in
        if check_in and check_out:
            if check_out <= check_in:
                raise serializers.ValidationError({
                    'check_out': 'Check-out date must be after check-in date.'
                })
        
        # Validate number of guests doesn't exceed listing capacity
        if listing and number_of_guests:
            if number_of_guests > listing.max_guests:
                raise serializers.ValidationError({
                    'number_of_guests': f'Number of guests ({number_of_guests}) exceeds maximum '
                                      f'guests allowed ({listing.max_guests}) for this listing.'
                })
        
        # Validate listing is available
        if listing and not listing.is_available:
            raise serializers.ValidationError({
                'listing': 'This listing is not currently available for booking.'
            })
        
        return data
    
    def validate_total_price(self, value):
        """Validate that total price is non-negative."""
        if value < 0:
            raise serializers.ValidationError("Total price must be non-negative.")
        return value
    
    def validate_number_of_guests(self, value):
        """Validate that number of guests is at least 1."""
        if value < 1:
            raise serializers.ValidationError("Number of guests must be at least 1.")
        return value


class BookingCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating bookings (simplified, without nested objects)."""
    
    listing_id = serializers.PrimaryKeyRelatedField(
        queryset=Listing.objects.filter(is_available=True),
        source='listing',
        required=True
    )
    guest_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='guest',
        required=True
    )
    
    class Meta:
        model = Booking
        fields = [
            'listing_id',
            'guest_id',
            'check_in',
            'check_out',
            'number_of_guests',
            'total_price',
            'special_requests',
        ]
    
    def validate(self, data):
        """Validate booking data."""
        check_in = data.get('check_in')
        check_out = data.get('check_out')
        listing = data.get('listing')
        number_of_guests = data.get('number_of_guests')
        
        # Validate check-out is after check-in
        if check_in and check_out:
            if check_out <= check_in:
                raise serializers.ValidationError({
                    'check_out': 'Check-out date must be after check-in date.'
                })
        
        # Validate number of guests doesn't exceed listing capacity
        if listing and number_of_guests:
            if number_of_guests > listing.max_guests:
                raise serializers.ValidationError({
                    'number_of_guests': f'Number of guests ({number_of_guests}) exceeds maximum '
                                      f'guests allowed ({listing.max_guests}) for this listing.'
                })
        
        # Validate listing is available
        if listing and not listing.is_available:
            raise serializers.ValidationError({
                'listing_id': 'This listing is not currently available for booking.'
            })
        
        return data

