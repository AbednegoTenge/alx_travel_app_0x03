from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from .models import Listing, Booking, Payment
from .serializers import ListingSerializer, BookingSerializer, PaymentSerializer, UserSerializer
from rest_framework.response import Response
from rest_framework import status
from .services.chapa_service import ChapaService
from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view
from .tasks import send_booking_confirmation_email

User = get_user_model()


# Create your views here.
class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class ListingViewSet(ModelViewSet):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer


class BookingViewSet(ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer


    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        booking = serilizer.save()

        booking_details = f"""
            Listing: {booking.listing.title}
            Check-in: {booking.check_in}
            Check-out: {booking.check_out}
            Guests: {booking.guest}
            Total Price: {booking.total_price}
        """

        # Send booking confirmation email asynchronously
        send_booking_confirmation_email.delay(
            user_email=booking.user.email,
            booking_details=str(booking)
        )

        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

class PaymentViewSet(ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        chapa_service = ChapaService()
        tx_ref = chapa_service.generate_tx_ref()

        try:
            chapa_response = chapa_service.initiate_payment(
                amount=str(data['amount']),
                currency="ETB",  # MUST be ETB or USD
                email=data['email'],
                first_name=data['first_name'],
                last_name=data['last_name'],
                tx_ref=tx_ref,
                callback_url="http://127.0.0.1:8000/api/payments/callback/",
                return_url="http://127.0.0.1:8000/payment/return/",
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        payment = Payment.objects.create(
            booking=data['booking'],
            transaction_id=tx_ref,
            chapa_reference=tx_ref,
            checkout_url=chapa_response["data"]["checkout_url"],
            amount=data['amount'],
            currency="ETB",
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
            phone_number=data.get('phone_number'),
            status="pending"
        )

        return Response(
            self.get_serializer(payment).data,
            status=status.HTTP_201_CREATED
        )

@api_view(['GET'])
def payment_return(request):
    return Response({
        "message": "Payment completed. You may close this page."
    })