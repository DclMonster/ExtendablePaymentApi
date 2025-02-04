"""Coinsub payment verification and API integration."""
import os
import hmac
import hashlib
import json
import requests
from typing import Dict, Any, Optional, List
from .abstract.signature_verifier import SignatureVerifier

class CoinsubVerificationError(Exception):
    """Base exception for Coinsub verification errors."""
    pass

class CoinsubVerifier(SignatureVerifier):
    """Verifier class for Coinsub webhook signatures and API integration."""
    
    _API_BASE = "https://api.coinsub.io"
    _CACHE: Dict[str, Any] = {}  # Cache for API responses

    def __init__(self) -> None:
        """Initialize the verifier with configuration from environment variables.
        
        Required environment variables:
        - COINSUB_SECRET: The webhook shared secret for signature verification
        - COINSUB_MERCHANT_ID: The unique identifier assigned to each merchant
        - COINSUB_API_KEY: The API key generated through the merchant dashboard
        """
        super().__init__('COINSUB_SECRET')
        self._merchant_id = os.getenv('COINSUB_MERCHANT_ID')
        self._api_key = os.getenv('COINSUB_API_KEY')
        
        if not self._merchant_id or not self._api_key:
            raise ValueError("COINSUB_MERCHANT_ID and COINSUB_API_KEY must be set in environment variables")

    def verify_signature(self, payload: Dict[str, Any], actual_signature: str | None) -> bool:
        """Verify the Coinsub webhook signature.

        Parameters
        ----------
        payload : Dict[str, Any]
            The payload of the webhook event
        actual_signature : str | None
            The actual signature to verify

        Returns
        -------
        bool
            True if the signature is valid, False otherwise
        """
        if not actual_signature:
            raise ValueError("Signature not provided")
        computed_signature = hmac.new(
            self._secret.encode(),
            json.dumps(payload).encode(),
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(computed_signature, actual_signature)

    def get_signature_from_header(self, header: Dict[str, str]) -> str:
        """Extract the signature from the header.
        
        Parameters
        ----------
        header : Dict[str, str]
            The header containing the signature
            
        Returns
        -------
        str
            The extracted signature
        """
        return header.get('COINSUB-SIGNATURE', '')

    def _get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers for API requests.
        
        Returns
        -------
        Dict[str, str]
            The authentication headers
        """
        return {
            'Merchant-ID': self._merchant_id,
            'API-Key': self._api_key,
            'Content-Type': 'application/json'
        }

    def verify_subscription(self, subscriber_id: str, product_id: str) -> Dict[str, Any]:
        """Verify a subscription status.
        
        Parameters
        ----------
        subscriber_id : str
            The ID of the subscriber
        product_id : str
            The ID of the product
            
        Returns
        -------
        Dict[str, Any]
            The subscription status data
            
        Raises
        ------
        CoinsubVerificationError
            If verification fails
        """
        try:
            response = requests.get(
                f"{self._API_BASE}/subscriptions/status",
                headers=self._get_auth_headers(),
                params={
                    'subscriber_id': subscriber_id,
                    'product_id': product_id
                }
            )
            
            if response.status_code != 200:
                raise CoinsubVerificationError(f"Subscription verification failed: {response.text}")
            
            return response.json()
        except Exception as e:
            raise CoinsubVerificationError(f"Subscription verification error: {str(e)}")

    def get_products(self) -> Dict[str, Any]:
        """Get the list of merchant products.
        
        Returns
        -------
        Dict[str, Any]
            The product list data
            
        Raises
        ------
        CoinsubVerificationError
            If retrieval fails
        """
        try:
            # Check cache first
            if 'products' in self._CACHE:
                return self._CACHE['products']
            
            response = requests.get(
                f"{self._API_BASE}/products",
                headers=self._get_auth_headers()
            )
            
            if response.status_code != 200:
                raise CoinsubVerificationError(f"Product retrieval failed: {response.text}")
            
            products = response.json()
            self._CACHE['products'] = products
            return products
        except Exception as e:
            raise CoinsubVerificationError(f"Product retrieval error: {str(e)}")

    def get_customer_data(self, subscriber_id: str) -> Dict[str, Any]:
        """Get customer subscription and purchase data.
        
        Parameters
        ----------
        subscriber_id : str
            The ID of the subscriber
            
        Returns
        -------
        Dict[str, Any]
            The customer data
            
        Raises
        ------
        CoinsubVerificationError
            If retrieval fails
        """
        try:
            response = requests.get(
                f"{self._API_BASE}/customers/{subscriber_id}",
                headers=self._get_auth_headers()
            )
            
            if response.status_code != 200:
                raise CoinsubVerificationError(f"Customer data retrieval failed: {response.text}")
            
            return response.json()
        except Exception as e:
            raise CoinsubVerificationError(f"Customer data retrieval error: {str(e)}")

    def verify_by_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Verify subscription status using metadata.
        
        Parameters
        ----------
        metadata : Dict[str, Any]
            The metadata to verify against
            
        Returns
        -------
        Dict[str, Any]
            The subscription status data
            
        Raises
        ------
        CoinsubVerificationError
            If verification fails
        """
        try:
            response = requests.post(
                f"{self._API_BASE}/subscriptions/verify",
                headers=self._get_auth_headers(),
                json={'metadata': metadata}
            )
            
            if response.status_code != 200:
                raise CoinsubVerificationError(f"Metadata verification failed: {response.text}")
            
            return response.json()
        except Exception as e:
            raise CoinsubVerificationError(f"Metadata verification error: {str(e)}")

    def clear_cache(self) -> None:
        """Clear the API response cache."""
        self._CACHE.clear()