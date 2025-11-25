"""
Django management command to seed the database with sample listings data.
Usage: python manage.py seed [--listings N] [--bookings] [--reviews]
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta
import random

from listings.models import Listing, Booking, Review


class Command(BaseCommand):
    help = 'Seed the database with sample listings, bookings, and reviews'

    def add_arguments(self, parser):
        parser.add_argument(
            '--listings',
            type=int,
            default=20,
            help='Number of listings to create (default: 20)',
        )
        parser.add_argument(
            '--bookings',
            action='store_true',
            help='Create sample bookings',
        )
        parser.add_argument(
            '--reviews',
            action='store_true',
            help='Create sample reviews',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding',
        )

    def handle(self, *args, **options):
        num_listings = options['listings']
        create_bookings = options['bookings']
        create_reviews = options['reviews']
        clear_data = options['clear']

        if clear_data:
            self.stdout.write(self.style.WARNING('Clearing existing data...'))
            Review.objects.all().delete()
            Booking.objects.all().delete()
            Listing.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Existing data cleared.'))

        # Create or get sample users (hosts)
        hosts = self._create_hosts()
        
        # Create listings
        self.stdout.write(f'Creating {num_listings} listings...')
        listings = self._create_listings(hosts, num_listings)
        self.stdout.write(self.style.SUCCESS(f'Successfully created {len(listings)} listings.'))

        # Create bookings if requested
        if create_bookings:
            self.stdout.write('Creating sample bookings...')
            bookings = self._create_bookings(listings, hosts)
            self.stdout.write(self.style.SUCCESS(f'Successfully created {len(bookings)} bookings.'))

        # Create reviews if requested
        if create_reviews:
            self.stdout.write('Creating sample reviews...')
            reviews = self._create_reviews(listings)
            self.stdout.write(self.style.SUCCESS(f'Successfully created {len(reviews)} reviews.'))

        self.stdout.write(self.style.SUCCESS('Database seeding completed!'))

    def _create_hosts(self):
        """Create or get sample host users."""
        hosts = []
        host_data = [
            {'username': 'host1', 'email': 'host1@example.com', 'first_name': 'John', 'last_name': 'Smith'},
            {'username': 'host2', 'email': 'host2@example.com', 'first_name': 'Sarah', 'last_name': 'Johnson'},
            {'username': 'host3', 'email': 'host3@example.com', 'first_name': 'Michael', 'last_name': 'Brown'},
            {'username': 'host4', 'email': 'host4@example.com', 'first_name': 'Emily', 'last_name': 'Davis'},
            {'username': 'host5', 'email': 'host5@example.com', 'first_name': 'David', 'last_name': 'Wilson'},
        ]

        for host_info in host_data:
            host, created = User.objects.get_or_create(
                username=host_info['username'],
                defaults={
                    'email': host_info['email'],
                    'first_name': host_info['first_name'],
                    'last_name': host_info['last_name'],
                }
            )
            if created:
                host.set_password('password123')
                host.save()
                self.stdout.write(f'Created host: {host.username}')
            hosts.append(host)

        return hosts

    def _create_listings(self, hosts, num_listings):
        """Create sample listings."""
        cities_data = [
            {'city': 'New York', 'country': 'United States'},
            {'city': 'London', 'country': 'United Kingdom'},
            {'city': 'Paris', 'country': 'France'},
            {'city': 'Tokyo', 'country': 'Japan'},
            {'city': 'Sydney', 'country': 'Australia'},
            {'city': 'Dubai', 'country': 'United Arab Emirates'},
            {'city': 'Barcelona', 'country': 'Spain'},
            {'city': 'Rome', 'country': 'Italy'},
            {'city': 'Bangkok', 'country': 'Thailand'},
            {'city': 'Amsterdam', 'country': 'Netherlands'},
            {'city': 'Berlin', 'country': 'Germany'},
            {'city': 'Singapore', 'country': 'Singapore'},
            {'city': 'Istanbul', 'country': 'Turkey'},
            {'city': 'Cairo', 'country': 'Egypt'},
            {'city': 'Cape Town', 'country': 'South Africa'},
        ]

        property_types = [choice[0] for choice in Listing.PROPERTY_TYPES]
        
        amenities_pool = [
            'WiFi', 'Air Conditioning', 'Heating', 'Kitchen', 'Washer', 'Dryer',
            'TV', 'Parking', 'Pool', 'Gym', 'Hot Tub', 'Fireplace', 'Balcony',
            'Garden', 'Beach Access', 'Mountain View', 'City View', 'Elevator',
            'Security System', 'Pet Friendly', 'Smoking Allowed', 'Wheelchair Accessible'
        ]

        titles_templates = {
            'apartment': [
                'Cozy Apartment in {city}',
                'Modern {city} Apartment',
                'Stylish Downtown {city} Apartment',
                'Luxury {city} Apartment',
                'Spacious {city} Apartment',
            ],
            'house': [
                'Beautiful House in {city}',
                'Family-Friendly {city} House',
                'Charming {city} Home',
                'Elegant {city} House',
                'Traditional {city} House',
            ],
            'hotel': [
                'Grand {city} Hotel',
                'Boutique {city} Hotel',
                'Luxury {city} Hotel',
                'Central {city} Hotel',
                'Historic {city} Hotel',
            ],
            'villa': [
                'Luxury Villa in {city}',
                'Private {city} Villa',
                'Beachfront {city} Villa',
                'Modern {city} Villa',
                'Elegant {city} Villa',
            ],
            'cottage': [
                'Charming Cottage in {city}',
                'Cozy {city} Cottage',
                'Rustic {city} Cottage',
                'Quaint {city} Cottage',
                'Traditional {city} Cottage',
            ],
            'hostel': [
                'Budget-Friendly {city} Hostel',
                'Central {city} Hostel',
                'Modern {city} Hostel',
                'Social {city} Hostel',
                'Clean {city} Hostel',
            ],
            'resort': [
                'Luxury {city} Resort',
                'Beach {city} Resort',
                'All-Inclusive {city} Resort',
                'Family {city} Resort',
                'Boutique {city} Resort',
            ],
        }

        descriptions = [
            'A beautiful and well-maintained property perfect for your stay. Located in a prime area with easy access to local attractions.',
            'Experience comfort and luxury in this stunning property. Fully equipped with modern amenities and excellent service.',
            'Perfect for families and groups. This spacious property offers everything you need for a memorable vacation.',
            'Located in the heart of the city, this property provides easy access to restaurants, shops, and cultural sites.',
            'A peaceful retreat offering tranquility and relaxation. Ideal for those seeking a quiet getaway.',
            'Modern design meets comfort in this exceptional property. Features top-of-the-line amenities and stunning views.',
            'Historic charm with modern conveniences. This unique property offers a one-of-a-kind experience.',
            'Beachfront property with breathtaking ocean views. Perfect for beach lovers and water sports enthusiasts.',
            'Mountain view property surrounded by nature. Great for hiking, outdoor activities, and nature lovers.',
            'Urban chic property in the city center. Close to nightlife, dining, and entertainment options.',
        ]

        listings = []
        for i in range(num_listings):
            city_data = random.choice(cities_data)
            property_type = random.choice(property_types)
            host = random.choice(hosts)
            
            # Generate title
            title_template = random.choice(titles_templates[property_type])
            title = title_template.format(city=city_data['city'])
            
            # Generate address
            street_number = random.randint(1, 9999)
            street_names = ['Main St', 'Park Ave', 'Broadway', 'Ocean Dr', 'Mountain Rd', 'Garden Ln', 'Sunset Blvd']
            address = f"{street_number} {random.choice(street_names)}"
            
            # Generate price based on property type
            price_ranges = {
                'hostel': (15, 50),
                'apartment': (50, 200),
                'house': (80, 300),
                'cottage': (60, 250),
                'hotel': (100, 400),
                'villa': (200, 800),
                'resort': (150, 600),
            }
            min_price, max_price = price_ranges.get(property_type, (50, 200))
            price_per_night = Decimal(str(random.randint(min_price, max_price)))
            
            # Generate property details
            if property_type in ['hostel']:
                bedrooms = random.randint(1, 4)
                bathrooms = random.randint(1, 2)
                max_guests = random.randint(2, 8)
            elif property_type in ['apartment', 'cottage']:
                bedrooms = random.randint(1, 3)
                bathrooms = random.randint(1, 2)
                max_guests = random.randint(2, 6)
            elif property_type in ['house', 'villa']:
                bedrooms = random.randint(2, 6)
                bathrooms = random.randint(2, 5)
                max_guests = random.randint(4, 12)
            else:  # hotel, resort
                bedrooms = random.randint(1, 4)
                bathrooms = random.randint(1, 3)
                max_guests = random.randint(2, 8)
            
            # Generate amenities
            num_amenities = random.randint(3, 8)
            amenities = random.sample(amenities_pool, min(num_amenities, len(amenities_pool)))
            
            # Generate description
            description = random.choice(descriptions)
            
            # Create listing
            listing = Listing.objects.create(
                host=host,
                title=title,
                description=description,
                address=address,
                city=city_data['city'],
                country=city_data['country'],
                property_type=property_type,
                price_per_night=price_per_night,
                max_guests=max_guests,
                bedrooms=bedrooms,
                bathrooms=bathrooms,
                amenities=amenities,
                is_available=random.choice([True, True, True, False]),  # 75% available
            )
            listings.append(listing)

        return listings

    def _create_bookings(self, listings, hosts):
        """Create sample bookings."""
        # Create guest users
        guests = []
        for i in range(1, 6):
            guest, created = User.objects.get_or_create(
                username=f'guest{i}',
                defaults={
                    'email': f'guest{i}@example.com',
                    'first_name': f'Guest{i}',
                    'last_name': 'User',
                }
            )
            if created:
                guest.set_password('password123')
                guest.save()
            guests.append(guest)

        bookings = []
        available_listings = [l for l in listings if l.is_available]
        
        if not available_listings:
            self.stdout.write(self.style.WARNING('No available listings to create bookings for.'))
            return bookings

        # Create bookings for past, present, and future dates
        today = timezone.now().date()
        
        for _ in range(min(15, len(available_listings) * 2)):
            listing = random.choice(available_listings)
            guest = random.choice(guests)
            
            # Random booking period
            days_ahead = random.randint(-30, 60)  # Past 30 days to future 60 days
            check_in = today + timedelta(days=days_ahead)
            nights = random.randint(1, 7)
            check_out = check_in + timedelta(days=nights)
            
            # Calculate total price
            total_price = listing.price_per_night * nights
            
            # Random status
            status = random.choice(['pending', 'confirmed', 'confirmed', 'completed', 'cancelled'])
            
            # Special requests (optional)
            special_requests = None
            if random.choice([True, False]):
                requests = [
                    'Late check-in requested',
                    'Early check-in if possible',
                    'Extra towels needed',
                    'Quiet room preferred',
                    'High floor preferred',
                ]
                special_requests = random.choice(requests)
            
            booking = Booking.objects.create(
                listing=listing,
                guest=guest,
                check_in=check_in,
                check_out=check_out,
                number_of_guests=random.randint(1, listing.max_guests),
                total_price=total_price,
                status=status,
                special_requests=special_requests,
            )
            bookings.append(booking)

        return bookings

    def _create_reviews(self, listings):
        """Create sample reviews."""
        # Get all users (hosts and guests)
        all_users = User.objects.all()
        
        if not all_users.exists():
            self.stdout.write(self.style.WARNING('No users found to create reviews.'))
            return []

        reviews = []
        ratings_comments = {
            5: [
                'Excellent stay! Highly recommended.',
                'Perfect location and amazing amenities.',
                'One of the best places I\'ve stayed.',
                'Absolutely wonderful experience!',
                'Exceeded all expectations.',
            ],
            4: [
                'Great place, would stay again.',
                'Nice property with good amenities.',
                'Comfortable and well-located.',
                'Good value for money.',
                'Enjoyed my stay here.',
            ],
            3: [
                'Decent place, nothing special.',
                'Average accommodation.',
                'It was okay, but could be better.',
                'Met basic expectations.',
            ],
            2: [
                'Not as expected.',
                'Some issues during the stay.',
                'Could use improvements.',
            ],
            1: [
                'Disappointing experience.',
                'Would not recommend.',
                'Many issues to address.',
            ],
        }

        # Create reviews for random listings
        for _ in range(min(20, len(listings) * 2)):
            listing = random.choice(listings)
            user = random.choice(all_users)
            
            # Check if user already reviewed this listing
            if Review.objects.filter(listing=listing, user=user).exists():
                continue
            
            # Random rating
            rating = random.choices(
                [5, 4, 3, 2, 1],
                weights=[40, 30, 15, 10, 5]  # More positive reviews
            )[0]
            
            comment = random.choice(ratings_comments[rating])
            
            # Try to associate with a booking if available
            booking = None
            user_bookings = Booking.objects.filter(guest=user, listing=listing, status='completed')
            if user_bookings.exists():
                booking = random.choice(user_bookings)
            
            review = Review.objects.create(
                listing=listing,
                user=user,
                booking=booking,
                rating=rating,
                comment=comment,
            )
            reviews.append(review)

        return reviews

