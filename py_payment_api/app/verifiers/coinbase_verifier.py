"""Coinbase Commerce webhook signature verifier."""
import os
import hmac
import hashlib
import json
import requests
from typing import Dict, Any, Optional, cast
from .abstract.signature_verifier import SignatureVerifier

class CoinbaseVerifier(SignatureVerifier):
    """
    Verifier class for Coinbase Commerce webhook signatures.
    Supports both live and sandbox environments.
    """
    
    _COMMERCE_API = "https://api.commerce.coinbase.com"
    _CERT_CACHE: Dict[str, str] = {}  # Cache for API responses

    def __init__(self) -> None:
        """
        Initializes the verifier with configuration from environment variables.
        
        Required environment variables:
        - COINBASE_SECRET: The webhook shared secret for signature verification
        - COINBASE_API_KEY: The Coinbase Commerce API key
        - COINBASE_SANDBOX_MODE: Whether to use sandbox mode (true/false)
        """
        super().__init__('COINBASE_SECRET')
        self._api_key = os.getenv('COINBASE_API_KEY')
        self._sandbox_mode = os.getenv('COINBASE_SANDBOX_MODE', 'false').lower() == 'true'
        
        if not self._api_key:
            raise ValueError("COINBASE_API_KEY not set in environment variables")

    def verify_signature(self, data: Dict[str, Any], signature: str) -> bool:
        """
        Verifies the signature of the webhook request.

        Parameters
        ----------
        data : Dict[str, Any]
            The raw request data
        signature : str
            The signature from the request headers

        Returns
        -------
        bool
            True if the signature is valid, False otherwise
        """
        try:
            # Create HMAC signature using the shared secret
            computed_signature = hmac.new(
                key=self._secret.encode(),
                msg=json.dumps(data).encode(),
                digestmod=hashlib.sha256
            ).hexdigest()
            
            # Use constant-time comparison to prevent timing attacks
            return hmac.compare_digest(computed_signature, signature)
        except Exception as e:
            print(f"Signature verification failed: {str(e)}")
            return False

    def get_signature_from_header(self, header: Dict[str, Any]) -> str:
        """
        Extracts the signature from the header.

        Parameters
        ----------
        header : Dict[str, Any]
            The header containing the signature

        Returns
        -------
        str
            The extracted signature

        Raises
        ------
        ValueError
            If the signature is missing or invalid
        """
        signature = header.get('X-CC-Webhook-Signature')
        if not signature:
            raise ValueError("Missing Coinbase signature in headers")
        if not isinstance(signature, str):
            raise ValueError("Invalid Coinbase signature format")
        return signature

    def verify_charge(self, charge_id: str) -> Dict[str, Any]:
        """
        Verifies a charge with the Coinbase Commerce API.

        Parameters
        ----------
        charge_id : str
            The charge ID to verify

        Returns
        -------
        Dict[str, Any]
            The charge data if valid

        Raises
        ------
        ValueError
            If charge verification fails
        """
        try:
            headers = self._get_auth_headers()
            response = requests.get(
                f"{self._COMMERCE_API}/charges/{charge_id}",
                headers=headers
            )
            
            if response.status_code != 200:
                raise ValueError(f"Charge verification failed: {response.text}")
            
            return response.json()['data']
        except Exception as e:
            raise ValueError(f"Charge verification error: {str(e)}")

    def create_charge(self, charge_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Creates a new charge using the Coinbase Commerce API.

        Parameters
        ----------
        charge_data : Dict[str, Any]
            The charge data to create. Should include:
            - name: Product/service name
            - description: Product description
            - pricing_type: fixed_price or no_price
            - local_price: Dict with amount and currency
            - metadata: Optional custom data

        Returns
        -------
        Dict[str, Any]
            The created charge data

        Raises
        ------
        ValueError
            If charge creation fails
        """
        try:
            headers = self._get_auth_headers()
            response = requests.post(
                f"{self._COMMERCE_API}/charges",
                headers=headers,
                json=charge_data
            )
            
            if response.status_code != 201:
                raise ValueError(f"Charge creation failed: {response.text}")
            
            return response.json()['data']
        except Exception as e:
            raise ValueError(f"Charge creation error: {str(e)}")

    def list_charges(self, limit: int = 25, starting_after: Optional[str] = None) -> Dict[str, Any]:
        """
        Lists charges from the Coinbase Commerce API.

        Parameters
        ----------
        limit : int, optional
            Number of charges to return (default: 25, max: 100)
        starting_after : str, optional
            Cursor for pagination

        Returns
        -------
        Dict[str, Any]
            List of charges and pagination info

        Raises
        ------
        ValueError
            If listing charges fails
        """
        try:
            headers = self._get_auth_headers()
            params = {'limit': min(limit, 100)}
            if starting_after:
                params['starting_after'] = starting_after
                
            response = requests.get(
                f"{self._COMMERCE_API}/charges",
                headers=headers,
                params=params
            )
            
            if response.status_code != 200:
                raise ValueError(f"Listing charges failed: {response.text}")
            
            return response.json()
        except Exception as e:
            raise ValueError(f"Listing charges error: {str(e)}")

    def _get_auth_headers(self) -> Dict[str, str]:
        """
        Gets the authentication headers for Coinbase Commerce API requests.

        Returns
        -------
        Dict[str, str]
            The authentication headers
        """
        return {
            'X-CC-Api-Key': self._api_key,
            'X-CC-Version': '2018-03-22',
            'Content-Type': 'application/json'
        } 