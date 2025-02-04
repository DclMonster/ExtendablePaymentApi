"""Google Play payment verification and API integration.

This module provides comprehensive verification and API integration for Google Play Store
in-app purchases and subscriptions.

API Docs: https://developer.android.com/google/play/developer-api
"""
import jwt
import os
import requests
import time
from typing import Any, Dict, Optional, List, Union
from .abstract.signature_verifier import SignatureVerifier
from services.logger import logger
from interfaces.payment.verify import VerifyResponse, OrderSchema, SubscriptionSchema
from google.oauth2 import service_account
from googleapiclient import discovery
from google.cloud import pubsub_v1
from datetime import datetime

class ProductType:
    """Product types in Google Play."""
    ONE_TIME = "ONE_TIME"
    SUBSCRIPTION = "SUBS"

class GoogleVerificationError(Exception):
    """Base exception for Google Play verification errors."""
    pass

class GoogleVerifier(SignatureVerifier):
    """
    Verifier class for Google Play webhook signatures and API integration.
    Supports both production and sandbox environments.
    
    This class handles all Google Play-related IAP requests, responses, and signature verification.
    It follows Google's best practices for subscription and purchase management.
    
    Attributes
    ----------
    _API_BASE : str
        Base URL for Google Play API
    _CACHE : Dict[str, Any]
        Cache for API responses to minimize unnecessary calls
    """
    
    _API_BASE = "https://androidpublisher.googleapis.com/androidpublisher/v3"
    _CACHE: Dict[str, Any] = {}
    _CACHE_DURATION = 3600  # 1 hour cache duration

    def __init__(self) -> None:
        """
        Initialize the verifier with configuration from environment variables.
        
        Required environment variables:
        - GOOGLE_PUBLIC_KEY: The public key for signature verification
        - GOOGLE_PACKAGE_NAME: The package name of your Android app
        - GOOGLE_SERVICE_ACCOUNT_KEY: Path to the service account key JSON
        - GOOGLE_SANDBOX_MODE: Whether to use sandbox mode (true/false)
        - GOOGLE_PROJECT_ID: The Google Cloud project ID
        - GOOGLE_SUBSCRIPTION_ID: The PubSub subscription ID for RTDNs
        
        Raises
        ------
        ValueError
            If required environment variables are missing
        """
        super().__init__('GOOGLE_PUBLIC_KEY')
        self._package_name = os.getenv('GOOGLE_PACKAGE_NAME')
        self._service_account_key_path = os.getenv('GOOGLE_SERVICE_ACCOUNT_KEY')
        self._sandbox_mode = os.getenv('GOOGLE_SANDBOX_MODE', 'false').lower() == 'true'
        self._project_id = os.getenv('GOOGLE_PROJECT_ID')
        self._subscription_id = os.getenv('GOOGLE_SUBSCRIPTION_ID')
        
        if not all([self._package_name, self._service_account_key_path]):
            raise ValueError("Missing required Google Play configuration")
            
        # Initialize API client
        self._initialize_api_client()

    def _initialize_api_client(self) -> None:
        """
        Initialize the Google Play API client with proper credentials.
        
        Raises
        ------
        GoogleVerificationError
            If client initialization fails
        """
        try:
            credentials = service_account.Credentials.from_service_account_file(
                self._service_account_key_path,
                scopes=['https://www.googleapis.com/auth/androidpublisher']
            )
            self._service = discovery.build(
                'androidpublisher',
                'v3',
                credentials=credentials,
                cache_discovery=False
            )
        except Exception as e:
            logger.error(f"Failed to initialize Google Play API client: {str(e)}")
            raise GoogleVerificationError("API client initialization failed")

    def verify_signature(self, data: Dict[str, Any], signature: str) -> bool:
        """
        Verify the signature of the webhook request.
        
        Parameters
        ----------
        data : Dict[str, Any]
            The signed payload from the event data
        signature : str
            The signature to verify
            
        Returns
        -------
        bool
            True if the signature is valid, False otherwise
        """
        try:
            jwt.decode(signature, self._secret, algorithms=['RS256'])
            return True
        except Exception as e:
            logger.error(f"Signature verification error: {str(e)}")
            return False

    async def verify_purchase(self, purchase_token: str, product_id: str) -> VerifyResponse:
        """
        Verify a one-time purchase.
        
        Parameters
        ----------
        purchase_token : str
            The purchase token to verify
        product_id : str
            The product ID
            
        Returns
        -------
        VerifyResponse
            Standardized response containing verification results
        """
        try:
            cache_key = f"purchase_{product_id}_{purchase_token}"
            if cache_key in self._CACHE:
                return self._CACHE[cache_key]
                
            response = (
                self._service.purchases()
                .products()
                .get(
                    packageName=self._package_name,
                    productId=product_id,
                    token=purchase_token
                )
                .execute()
            )
            
            order_data = OrderSchema(
                product_id=product_id,
                transaction_id=response.get('orderId'),
                purchase_date=response.get('purchaseTimeMillis'),
                qty=response.get('quantity', 1),
                refundable_qty=response.get('refundableQuantity')
            )
            
            result = {
                "status": "success",
                "error": None,
                "type": "product",
                "item": order_data,
                "subscription": None,
                "state": response.get('purchaseState'),
                "purchase_token": purchase_token
            }
            
            self._CACHE[cache_key] = result
            return result
            
        except Exception as e:
            logger.error(f"Purchase verification error: {str(e)}")
            return {
                "status": "error",
                "error": {"msg": str(e)},
                "type": "unknown",
                "item": None,
                "subscription": None,
                "state": None,
                "purchase_token": None
            }

    async def verify_subscription(self, purchase_token: str, subscription_id: str) -> VerifyResponse:
        """
        Verify a subscription purchase.
        
        Parameters
        ----------
        purchase_token : str
            The purchase token to verify
        subscription_id : str
            The subscription ID
            
        Returns
        -------
        VerifyResponse
            Standardized response containing verification results
        """
        try:
            cache_key = f"subscription_{subscription_id}_{purchase_token}"
            if cache_key in self._CACHE:
                return self._CACHE[cache_key]
                
            response = (
                self._service.purchases()
                .subscriptionsv2()
                .get(
                    packageName=self._package_name,
                    token=purchase_token
                )
                .execute()
            )
            
            subscription_data = SubscriptionSchema(
                product_id=subscription_id,
                transaction_id=response.get('orderId'),
                start_date=response.get('startTimeMillis'),
                expires_date=response.get('expiryTimeMillis'),
                subscription_group_identifier=None,
                renewable=response.get('autoRenewing', False),
                status=response.get('paymentState', 'unknown')
            )
            
            result = {
                "status": "success",
                "error": None,
                "type": "subscription",
                "item": None,
                "subscription": subscription_data,
                "state": None,
                "purchase_token": purchase_token
            }
            
            self._CACHE[cache_key] = result
            return result
            
        except Exception as e:
            logger.error(f"Subscription verification error: {str(e)}")
            return {
                "status": "error",
                "error": {"msg": str(e)},
                "type": "unknown",
                "item": None,
                "subscription": None,
                "state": None,
                "purchase_token": None
            }

    def get_voided_purchases(self, start_time: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get a list of voided purchases.
        
        Following Google's best practices, this should be used to implement
        a revocation system that prevents access to voided purchases.
        
        Parameters
        ----------
        start_time : Optional[str]
            The start time for the query (RFC3339 timestamp)
            
        Returns
        -------
        List[Dict[str, Any]]
            The list of voided purchases
        """
        try:
            params = {'startTime': start_time} if start_time else {}
            response = (
                self._service.purchases()
                .voidedpurchases()
                .list(
                    packageName=self._package_name,
                    **params
                )
                .execute()
            )
            
            return response.get('voidedPurchases', [])
            
        except Exception as e:
            logger.error(f"Error retrieving voided purchases: {str(e)}")
            return []

    def acknowledge_purchase(self, purchase_token: str, product_id: str, is_subscription: bool = False) -> bool:
        """
        Acknowledge a purchase or subscription.
        
        Parameters
        ----------
        purchase_token : str
            The purchase token to acknowledge
        product_id : str
            The product ID
        is_subscription : bool
            Whether this is a subscription acknowledgment
            
        Returns
        -------
        bool
            True if acknowledgment was successful
        """
        try:
            if is_subscription:
                self._service.purchases().subscriptions().acknowledge(
                    packageName=self._package_name,
                    subscriptionId=product_id,
                    token=purchase_token
                ).execute()
            else:
                self._service.purchases().products().acknowledge(
                    packageName=self._package_name,
                    productId=product_id,
                    token=purchase_token
                ).execute()
            return True
        except Exception as e:
            logger.error(f"Purchase acknowledgment error: {str(e)}")
            return False

    def setup_real_time_developer_notifications(self) -> None:
        """
        Set up Real-time Developer Notifications (RTDN) using Cloud Pub/Sub.
        
        This follows Google's best practice of using RTDNs instead of polling
        for subscription status.
        """
        try:
            if not all([self._project_id, self._subscription_id]):
                raise ValueError("Missing Pub/Sub configuration")
                
            credentials = service_account.Credentials.from_service_account_file(
                self._service_account_key_path
            )
            subscriber = pubsub_v1.SubscriberClient(credentials=credentials)
            subscription_path = subscriber.subscription_path(
                self._project_id,
                self._subscription_id
            )
            
            logger.info(f"RTDN setup complete. Listening on {subscription_path}")
            
        except Exception as e:
            logger.error(f"RTDN setup error: {str(e)}")
            raise GoogleVerificationError("Failed to set up RTDN")

    def clear_cache(self) -> None:
        """Clear the API response cache."""
        self._CACHE.clear()

    def _is_cache_valid(self, timestamp: float) -> bool:
        """Check if a cached item is still valid."""
        return (time.time() - timestamp) < self._CACHE_DURATION 

    async def create_product(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new in-app product in Google Play.
        
        Parameters
        ----------
        product_data : Dict[str, Any]
            Product details including:
            - product_id: str
            - name: str
            - description: str
            - price_micros: int
            - type: str (ONE_TIME or SUBS)
            
        Returns
        -------
        Dict[str, Any]
            The created product details
        """
        try:
            product_body = {
                "packageName": self._package_name,
                "productId": product_data["product_id"],
                "listing": {
                    "title": product_data["name"],
                    "description": product_data["description"]
                },
                "defaultPrice": {
                    "priceMicros": str(product_data["price_micros"]),
                    "currency": "USD"
                },
                "purchaseType": "managedUser",
                "status": "active"
            }
            
            response = (
                self._service.inappproducts()
                .insert(
                    packageName=self._package_name,
                    body=product_body,
                    autoConvertMissingPrices=True
                )
                .execute()
            )
            
            logger.info(f"Created product: {response}")
            return response
            
        except Exception as e:
            logger.error(f"Error creating product: {str(e)}")
            raise GoogleVerificationError(f"Product creation failed: {str(e)}")

    async def create_subscription(self, subscription_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new subscription in Google Play.
        
        Parameters
        ----------
        subscription_data : Dict[str, Any]
            Subscription details including:
            - subscription_id: str
            - name: str
            - description: str
            - price_micros: int
            - billing_period: str
            - grace_period: str
            
        Returns
        -------
        Dict[str, Any]
            The created subscription details
        """
        try:
            subscription_body = {
                "packageName": self._package_name,
                "subscriptionId": subscription_data["subscription_id"],
                "listing": {
                    "title": subscription_data["name"],
                    "description": subscription_data["description"]
                },
                "defaultPrice": {
                    "priceMicros": str(subscription_data["price_micros"]),
                    "currency": "USD"
                },
                "subscriptionPeriod": subscription_data["billing_period"],
                "gracePeriod": subscription_data.get("grace_period", "P0D"),
                "status": "active"
            }
            
            response = (
                self._service.monetization()
                .subscriptions()
                .create(
                    packageName=self._package_name,
                    body=subscription_body
                )
                .execute()
            )
            
            logger.info(f"Created subscription: {response}")
            return response
            
        except Exception as e:
            logger.error(f"Error creating subscription: {str(e)}")
            raise GoogleVerificationError(f"Subscription creation failed: {str(e)}")

    async def update_product(self, product_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing product in Google Play.
        
        Parameters
        ----------
        product_id : str
            The ID of the product to update
        update_data : Dict[str, Any]
            The data to update
            
        Returns
        -------
        Dict[str, Any]
            The updated product details
        """
        try:
            response = (
                self._service.inappproducts()
                .patch(
                    packageName=self._package_name,
                    productId=product_id,
                    body=update_data,
                    autoConvertMissingPrices=True
                )
                .execute()
            )
            
            logger.info(f"Updated product {product_id}: {response}")
            return response
            
        except Exception as e:
            logger.error(f"Error updating product: {str(e)}")
            raise GoogleVerificationError(f"Product update failed: {str(e)}")

    async def get_product_details(self, product_id: str) -> Dict[str, Any]:
        """
        Get details of a specific product.
        
        Parameters
        ----------
        product_id : str
            The ID of the product
            
        Returns
        -------
        Dict[str, Any]
            The product details
        """
        try:
            cache_key = f"product_details_{product_id}"
            if cache_key in self._CACHE:
                return self._CACHE[cache_key]
                
            response = (
                self._service.inappproducts()
                .get(
                    packageName=self._package_name,
                    productId=product_id
                )
                .execute()
            )
            
            self._CACHE[cache_key] = response
            return response
            
        except Exception as e:
            logger.error(f"Error getting product details: {str(e)}")
            raise GoogleVerificationError(f"Failed to get product details: {str(e)}")

    async def get_subscription_details(self, subscription_id: str) -> Dict[str, Any]:
        """
        Get details of a specific subscription.
        
        Parameters
        ----------
        subscription_id : str
            The ID of the subscription
            
        Returns
        -------
        Dict[str, Any]
            The subscription details
        """
        try:
            cache_key = f"subscription_details_{subscription_id}"
            if cache_key in self._CACHE:
                return self._CACHE[cache_key]
                
            response = (
                self._service.monetization()
                .subscriptions()
                .get(
                    packageName=self._package_name,
                    productId=subscription_id
                )
                .execute()
            )
            
            self._CACHE[cache_key] = response
            return response
            
        except Exception as e:
            logger.error(f"Error getting subscription details: {str(e)}")
            raise GoogleVerificationError(f"Failed to get subscription details: {str(e)}")

    async def list_products(self) -> List[Dict[str, Any]]:
        """
        List all in-app products.
        
        Returns
        -------
        List[Dict[str, Any]]
            List of all products
        """
        try:
            response = (
                self._service.inappproducts()
                .list(packageName=self._package_name)
                .execute()
            )
            
            return response.get("inappproduct", [])
            
        except Exception as e:
            logger.error(f"Error listing products: {str(e)}")
            raise GoogleVerificationError(f"Failed to list products: {str(e)}")

    async def list_subscriptions(self) -> List[Dict[str, Any]]:
        """
        List all subscriptions.
        
        Returns
        -------
        List[Dict[str, Any]]
            List of all subscriptions
        """
        try:
            response = (
                self._service.monetization()
                .subscriptions()
                .list(packageName=self._package_name)
                .execute()
            )
            
            return response.get("subscriptions", [])
            
        except Exception as e:
            logger.error(f"Error listing subscriptions: {str(e)}")
            raise GoogleVerificationError(f"Failed to list subscriptions: {str(e)}") 