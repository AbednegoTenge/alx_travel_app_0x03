import requests
import logging
import uuid
from typing import Dict, Optional
from dotenv import load_dotenv
import os

load_dotenv()


logger = logging.getLogger(__name__)


class ChapaService:
    """Service class for handling Chapa payment operations"""
    
    def __init__(self):
        self.secret_key = os.getenv("CHAPA_SECRET_KEY")
        self.base_url = os.getenv("CHAPA_BASE_URL")
        self.headers = {
            'Authorization': f'Bearer {self.secret_key}',
            'Content-Type': 'application/json'
        }
    
    def generate_tx_ref(self) -> str:
        """Generate a unique transaction reference"""
        return f"alx-travel-{uuid.uuid4().hex[:12]}"
    
    def initiate_payment(
        self,
        amount: float,
        currency: str,
        email: str,
        first_name: str,
        last_name: str,
        tx_ref: str,
        callback_url: str,
        return_url: str,
        customization: Optional[Dict] = None,
        phone_number: Optional[str] = None
    ) -> Dict:
        """
        Initiate a payment with Chapa
        
        Args:
            amount: Payment amount
            currency: Currency code (ETB, USD, etc.)
            email: Customer email
            first_name: Customer first name
            last_name: Customer last name
            tx_ref: Unique transaction reference
            callback_url: URL for Chapa to send payment status
            return_url: URL to redirect customer after payment
            customization: Optional dict with title, description, logo
            phone_number: Optional customer phone number
            
        Returns:
            Dict containing payment initialization response
        """
        endpoint = f"{self.base_url}/transaction/initialize"
        
        payload = {
            "amount": str(amount),
            "currency": currency,
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "tx_ref": tx_ref,
            "callback_url": callback_url,
            "return_url": return_url,
            "customization": {
                "title": "ALX Travel Booking",
                "description": "Payment for travel booking"
            }
        }
        
        if phone_number:
            payload["phone_number"] = phone_number
        
        if customization:
            payload["customization"] = customization
        
        try:
            response = requests.post(
                endpoint,
                json=payload,
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Chapa payment initiation failed: {str(e)}")
            raise Exception(f"Payment initiation failed: {str(e)}")
    
    def verify_payment(self, tx_ref: str) -> Dict:
        """
        Verify payment status with Chapa
        
        Args:
            tx_ref: Transaction reference to verify
            
        Returns:
            Dict containing payment verification response
        """
        endpoint = f"{self.base_url}/transaction/verify/{tx_ref}"
        
        try:
            response = requests.get(
                endpoint,
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Chapa payment verification failed: {str(e)}")
            raise Exception(f"Payment verification failed: {str(e)}")
    
    def get_banks(self) -> Dict:
        """Get list of available banks for direct bank transfers"""
        endpoint = f"{self.base_url}/banks"
        
        try:
            response = requests.get(
                endpoint,
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch banks: {str(e)}")
            raise Exception(f"Failed to fetch banks: {str(e)}")
