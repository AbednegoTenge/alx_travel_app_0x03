from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from .models import Listing, Booking
from .serializers import ListingSerializer, BookingSerializer


# Create your views here.
class ListingViewSet(ModelViewSet):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer


class BookingViewSet(ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer