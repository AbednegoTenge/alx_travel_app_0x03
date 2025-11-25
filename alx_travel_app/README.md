# ALX Travel App

A Django REST Framework-based travel accommodation booking application that allows users to list properties, make bookings, and leave reviews.

## Features

- **Listings Management**: Create and manage travel accommodation listings (apartments, houses, hotels, villas, cottages, hostels, resorts)
- **Booking System**: Make reservations with check-in/check-out dates, guest counts, and special requests
- **Review System**: Users can rate and review listings
- **RESTful API**: Full REST API with Django REST Framework
- **Database Seeding**: Management command to populate database with sample data
- **Admin Interface**: Django admin interface for managing data

## Technologies Used

- **Django 5.2.7**: Web framework
- **Django REST Framework**: API development
- **MySQL**: Database
- **Celery**: Asynchronous task queue
- **django-environ**: Environment variable management
- **django-cors-headers**: CORS handling
- **drf-yasg**: API documentation (Swagger/OpenAPI)

## Requirements

- Python 3.8+
- MySQL 5.7+ or MySQL 8.0+
- RabbitMQ (for Celery, optional)

## Installation

### 1. Clone the repository

```bash
cd alx_travel_app_0x00
```

### 2. Create and activate virtual environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r alx_travel_app/requirement.txt
```

**Note:** If you encounter issues installing `mysqlclient` on Windows, you can use `pymysql` instead:
```bash
pip install pymysql
```

Then add this to your `settings.py` before the database configuration:
```python
import pymysql
pymysql.install_as_MySQLdb()
```

### 4. Environment Variables

Create a `.env` file in the project root (`alx_travel_app_0x00/.env`) with the following variables:

```env
SECRET=your-secret-key-here
DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_HOST=localhost
DB_PORT=3306
```

**Generate a secret key:**
```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

### 5. Database Setup

1. Create a MySQL database:
```sql
CREATE DATABASE your_database_name CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

2. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create superuser (optional)

```bash
python manage.py createsuperuser
```

## Usage

### Seed Database with Sample Data

Populate the database with sample listings, bookings, and reviews:

```bash
# Create 20 listings (default)
python manage.py seed

# Create 50 listings
python manage.py seed --listings 50

# Create listings, bookings, and reviews
python manage.py seed --listings 30 --bookings --reviews

# Clear existing data and reseed
python manage.py seed --clear --listings 25 --bookings --reviews
```

### Run Development Server

```bash
python manage.py runserver
```

The server will start at `http://127.0.0.1:8000/`

### Access Admin Interface

Navigate to `http://127.0.0.1:8000/admin/` and login with your superuser credentials.

### API Documentation

If `drf-yasg` is configured, API documentation will be available at:
- Swagger UI: `http://127.0.0.1:8000/swagger/`
- ReDoc: `http://127.0.0.1:8000/redoc/`

## Project Structure

```
alx_travel_app/
├── __init__.py
├── settings.py          # Django settings
├── urls.py              # Main URL configuration
├── wsgi.py              # WSGI configuration
├── asgi.py              # ASGI configuration
├── celery.py            # Celery configuration
├── requirement.txt      # Python dependencies
├── README.md            # This file
│
└── listings/            # Main app
    ├── models.py        # Listing, Booking, Review models
    ├── serializers.py   # DRF serializers
    ├── views.py         # API views
    ├── admin.py         # Admin configuration
    ├── urls.py          # App URLs (if exists)
    │
    └── management/
        └── commands/
            └── seed.py  # Database seeding command
```

## Models

### Listing
- Accommodation listings with details like title, description, address, city, country
- Property types: apartment, house, hotel, villa, cottage, hostel, resort
- Pricing, amenities, guest capacity, bedrooms, bathrooms
- Host relationship (ForeignKey to User)

### Booking
- Reservations with check-in/check-out dates
- Guest count, total price, status (pending, confirmed, cancelled, completed)
- Special requests support
- Relationships: Listing, Guest (User)

### Review
- Ratings (1-5 stars) and comments
- Optional booking association
- Unique constraint: one review per user per listing
- Relationships: Listing, User, Booking (optional)

## API Endpoints

The API endpoints will be defined in your views. Common endpoints would include:

- `GET /api/listings/` - List all listings
- `POST /api/listings/` - Create a listing
- `GET /api/listings/{id}/` - Get listing details
- `PUT /api/listings/{id}/` - Update listing
- `DELETE /api/listings/{id}/` - Delete listing
- `GET /api/bookings/` - List bookings
- `POST /api/bookings/` - Create booking
- `GET /api/reviews/` - List reviews
- `POST /api/reviews/` - Create review

## Celery Setup (Optional)

If you want to use Celery for asynchronous tasks:

1. Install and start RabbitMQ:
```bash
# Windows: Download and install from https://www.rabbitmq.com/
# Linux: sudo apt-get install rabbitmq-server
# Mac: brew install rabbitmq
```

2. Start Celery worker:
```bash
celery -A alx_travel_app worker -l info
```

## Troubleshooting

### ModuleNotFoundError: No module named 'environ'
```bash
pip install django-environ
```

### ModuleNotFoundError: No module named 'corsheaders'
```bash
pip install django-cors-headers
```

### MySQL Connection Issues
- Ensure MySQL server is running
- Verify database credentials in `.env` file
- Check database exists and user has proper permissions

### Migration Issues
```bash
# Reset migrations (development only)
python manage.py migrate listings zero
python manage.py makemigrations listings
python manage.py migrate
```

## Development

### Running Tests
```bash
python manage.py test
```

### Code Style
Follow PEP 8 Python style guide.

## License

This project is part of the ALX Software Engineering program.

## Author

ALX Travel App Development Team

