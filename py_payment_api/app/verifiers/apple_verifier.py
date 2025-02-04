import jwt
import os
import requests
import time
from typing import Dict, Any, Optional, List, Union
from .abstract.signature_verifier import SignatureVerifier
from services.logger import logger
from interfaces.payment.verify import VerifyResponse, OrderSchema, SubscriptionSchema

class AppleVerifier(SignatureVerifier):
    """
    Verifier class for Apple webhook signatures and App Store Connect API integration.
    
    This class handles all Apple-related IAP requests, responses, and signature verification.
    It supports both one-time purchases and subscriptions.
    
    API Docs: https://developer.apple.com/documentation/appstoreserverapi
    
    Attributes
    ----------
    _APPLE_ROOT_CA_G3 : str
        URL for Apple Root CA G3 certificate
    _APPLE_AAI_CA : str
        URL for Apple AAI CA certificate
    _APPLE_STORE_CONNECT_API : str
        Base URL for App Store Connect API
    """
    
    _APPLE_ROOT_CA_G3 = "https://www.apple.com/certificateauthority/AppleRootCA-G3.cer"
    _APPLE_AAI_CA = "https://www.apple.com/certificateauthority/AppleAAICA.cer"
    _APPLE_STORE_CONNECT_API = "https://api.storekit.itunes.apple.com/inApps/v1"
    _APPLE_SANDBOX_API = "https://api.sandbox.storekit.itunes.apple.com/inApps/v1"

    def __init__(self) -> None:
        """
        Initializes the verifier with required configuration from environment variables.
        
        Required environment variables:
        - APPLE_PUBLIC_KEY: The public key for signature verification
        - APPLE_KEY_ID: The key ID for App Store Connect API
        - APPLE_ISSUER_ID: The issuer ID for App Store Connect API
        - APPLE_BUNDLE_ID: Your app's bundle ID
        - APPLE_ENVIRONMENT: 'sandbox' or 'production'
        
        Raises
        ------
        ValueError
            If any required environment variables are missing
        """
        super().__init__('APPLE_PUBLIC_KEY')
        self._key_id = os.getenv('APPLE_KEY_ID')
        self._issuer_id = os.getenv('APPLE_ISSUER_ID')
        self._bundle_id = os.getenv('APPLE_BUNDLE_ID', 'com.exodus.mobile.core')
        self._environment = os.getenv('APPLE_ENVIRONMENT', 'sandbox')
        
        if not all([self._key_id, self._issuer_id]):
            raise ValueError("Missing required Apple configuration in environment variables")
            
        # Set API base URL based on environment
        self._api_base_url = self._APPLE_SANDBOX_API if self._environment == 'sandbox' else self._APPLE_STORE_CONNECT_API
        
        # Initialize root certificates
        self._root_certificates = self._initialize_root_certificates()

    def _initialize_root_certificates(self) -> List[bytes]:
        """
        Initialize root certificates for signature verification.
        
        Returns
        -------
        List[bytes]
            List of root certificate contents
        """
        try:
            root_cert = requests.get(self._APPLE_ROOT_CA_G3).content
            aai_cert = requests.get(self._APPLE_AAI_CA).content
            return [root_cert, aai_cert]
        except Exception as e:
            logger.error(f"Error initializing root certificates: {str(e)}")
            raise ValueError("Failed to initialize root certificates")

    async def verify_receipt(self, receipt_data: str) -> VerifyResponse:
        """
        Verifies an App Store receipt using the App Store Connect API.
        
        Parameters
        ----------
        receipt_data : str
            The base64 encoded receipt data
            
        Returns
        -------
        VerifyResponse
            Standardized response containing verification results
            
        Example
        -------
        {
            "status": "success" or "error",
            "subscription": {
                "product_id": str,
                "transaction_id": str,
                "start_date": str,
                "expires_date": str,
                "subscription_group_identifier": str,
                "renewable": bool,
                "status": str
            } or None,
            "type": str,
            "error": None or Dict[str, Any],
            "item": {
                "product_id": str,
                "transaction_id": str,
                "purchase_date": str,
                "qty": int
            } or None
        }
        """
        try:
            token = self._generate_api_token()
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(
                f"{self._api_base_url}/receipts/verify",
                headers=headers,
                json={'receipt-data': receipt_data, 'password': self._secret}
            )
            
            if response.status_code != 200:
                logger.error(f"Receipt verification failed: {response.text}")
                return {
                    "status": "error",
                    "error": {"msg": response.text},
                    "type": "unknown",
                    "item": None,
                    "subscription": None,
                    "state": None,
                    "purchase_token": None
                }
            
            receipt_info = response.json()
            
            # Check if it's a subscription
            if receipt_info.get("auto_renew_status") is not None:
                subscription_data = SubscriptionSchema(
                    product_id=receipt_info["product_id"],
                    transaction_id=receipt_info["transaction_id"],
                    start_date=receipt_info["purchase_date"],
                    expires_date=receipt_info["expires_date"],
                    subscription_group_identifier=receipt_info.get("subscription_group_identifier"),
                    renewable=bool(receipt_info["auto_renew_status"]),
                    status="active" if receipt_info.get("expires_date", 0) > time.time() else "expired"
                )
                return {
                    "status": "success",
                    "subscription": subscription_data,
                    "type": "subscription",
                    "error": None,
                    "item": None,
                    "state": None,
                    "purchase_token": None
                }
            
            # One-time purchase
            order_data = OrderSchema(
                product_id=receipt_info["product_id"],
                transaction_id=receipt_info["transaction_id"],
                purchase_date=receipt_info["purchase_date"],
                qty=receipt_info.get("quantity", 1),
                refundable_qty=receipt_info.get("refundable_quantity")
            )
            
            return {
                "status": "success",
                "item": order_data,
                "type": "non-consumable",
                "error": None,
                "subscription": None,
                "state": None,
                "purchase_token": None
            }
            
        except Exception as e:
            logger.error(f"Receipt verification error: {str(e)}")
            return {
                "status": "error",
                "error": {"msg": str(e)},
                "type": "unknown",
                "item": None,
                "subscription": None,
                "state": None,
                "purchase_token": None
            }

    def verify_signature(self, data: Dict[str, Any], signature: str) -> bool:
        """
        Verifies the signature of the webhook request using JWS.
        
        Parameters
        ----------
        data : Dict[str, Any]
            The signed payload from the event data
        signature : str
            The JWS signature to verify
            
        Returns
        -------
        bool
            True if the signature is valid, False otherwise
        """
        try:
            decoded = jwt.decode(
                signature, 
                self._secret, 
                algorithms=['ES256'],
                audience=data.get('transactionId'),
                options={
                    'verify_exp': True,
                    'verify_aud': True,
                    'verify_iss': True
                }
            )
            
            return self._validate_decoded_payload(decoded, data)
            
        except Exception as e:
            logger.error(f"Signature verification error: {str(e)}")
            return False

    def notification_handler(self, json_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle notification from Apple App Store.
        
        Parameters
        ----------
        json_payload : Dict[str, Any]
            The notification payload from Apple
            
        Returns
        -------
        Dict[str, Any]
            Processed notification response
            
        Example
        -------
        {
            "status": "update" | "action_update" | "error" | "testing",
            "type": str,
            "update_body": Dict[str, Any],
            "identifier": {
                "transaction_id": str,
                "product_id": str
            }
        }
        """
        try:
            if not self.verify_signature(json_payload.get("data", {}), json_payload.get("signature", "")):
                return {
                    "status": "error",
                    "type": "verification_failed",
                    "update_body": {},
                    "identifier": None
                }
            
            notification_type = json_payload.get("notificationType")
            if not notification_type:
                return {
                    "status": "error",
                    "type": "invalid_notification",
                    "update_body": {},
                    "identifier": None
                }
                
            # Process different notification types
            if notification_type == "RENEWAL":
                return self._handle_renewal_notification(json_payload)
            elif notification_type == "REFUND":
                return self._handle_refund_notification(json_payload)
            elif notification_type == "EXPIRED":
                return self._handle_expiration_notification(json_payload)
            elif notification_type == "TEST":
                return {
                    "status": "testing",
                    "type": "test_notification",
                    "update_body": json_payload,
                    "identifier": None
                }
            
            return {
                "status": "error",
                "type": "unknown_notification_type",
                "update_body": {},
                "identifier": None
            }
            
        except Exception as e:
            logger.error(f"Notification handling error: {str(e)}")
            return {
                "status": "error",
                "type": "processing_error",
                "update_body": {"error": str(e)},
                "identifier": None
            }

    def _handle_renewal_notification(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle subscription renewal notifications"""
        transaction_info = payload.get("data", {}).get("signedTransactionInfo", {})
        return {
            "status": "action_update",
            "type": "subscription_renewed",
            "update_body": {
                "status": "active",
                "expires_date": transaction_info.get("expiresDate"),
                "renewable": True
            },
            "identifier": {
                "transaction_id": transaction_info.get("originalTransactionId"),
                "product_id": transaction_info.get("productId")
            }
        }

    def _handle_refund_notification(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle refund notifications"""
        transaction_info = payload.get("data", {}).get("signedTransactionInfo", {})
        return {
            "status": "action_update",
            "type": "refund",
            "update_body": {
                "status": "refunded",
                "refund_date": transaction_info.get("revocationDate")
            },
            "identifier": {
                "transaction_id": transaction_info.get("originalTransactionId"),
                "product_id": transaction_info.get("productId")
            }
        }

    def _handle_expiration_notification(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle subscription expiration notifications"""
        transaction_info = payload.get("data", {}).get("signedTransactionInfo", {})
        return {
            "status": "action_update",
            "type": "subscription_expired",
            "update_body": {
                "status": "expired",
                "expires_date": transaction_info.get("expiresDate"),
                "renewable": False
            },
            "identifier": {
                "transaction_id": transaction_info.get("originalTransactionId"),
                "product_id": transaction_info.get("productId")
            }
        }

    def _validate_decoded_payload(self, decoded: Dict[str, Any], original_data: Dict[str, Any]) -> bool:
        """
        Validates the decoded JWS payload against the original data.
        
        Parameters
        ----------
        decoded : Dict[str, Any]
            The decoded JWS payload
        original_data : Dict[str, Any]
            The original webhook data
            
        Returns
        -------
        bool
            True if the payload is valid, False otherwise
        """
        required_fields = ['iss', 'iat', 'exp', 'aud']
        if not all(field in decoded for field in required_fields):
            return False
            
        if decoded.get('iss') != 'Apple Inc.':
            return False
            
        if decoded.get('aud') != original_data.get('transactionId'):
            return False
            
        return True

    def _generate_api_token(self) -> str:
        """
        Generates a JWT token for App Store Connect API authentication.
        
        Returns
        -------
        str
            The generated JWT token
        """
        now = int(time.time())
        payload = {
            'iss': self._issuer_id,
            'iat': now,
            'exp': now + 3600,  # Token expires in 1 hour
            'aud': 'appstoreconnect-v1',
            'bid': self._bundle_id
        }
        
        return jwt.encode(
            payload,
            self._secret,
            algorithm='ES256',
            headers={'kid': self._key_id}
        )