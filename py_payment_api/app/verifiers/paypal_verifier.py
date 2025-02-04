"""PayPal webhook signature verifier."""
import os
import base64
import requests
from typing import Dict, Any, Optional, cast
from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.backends import default_backend
from .abstract.signature_verifier import SignatureVerifier

class PayPalVerifier(SignatureVerifier):
    """
    Verifier class for PayPal webhook signatures.
    Supports both live and sandbox environments.
    """
    
    _SANDBOX_API = "https://api.sandbox.paypal.com/v1"
    _LIVE_API = "https://api.paypal.com/v1"
    _CERT_CACHE: Dict[str, x509.Certificate] = {}  # Cache for certificates

    def __init__(self) -> None:
        """
        Initializes the verifier with configuration from environment variables.
        
        Required environment variables:
        - PAYPAL_SECRET: The PayPal client secret
        - PAYPAL_WEBHOOK_ID: The webhook ID for signature verification
        - PAYPAL_SANDBOX_MODE: Whether to use sandbox mode (true/false)
        """
        super().__init__("PAYPAL_SECRET")
        self._webhook_id = os.getenv("PAYPAL_WEBHOOK_ID")
        self._sandbox_mode = os.getenv("PAYPAL_SANDBOX_MODE", "false").lower() == "true"
        
        if not self._webhook_id:
            raise ValueError("PAYPAL_WEBHOOK_ID not set in environment variables")

    @property
    def api_base_url(self) -> str:
        """Get the base API URL based on environment."""
        return self._SANDBOX_API if self._sandbox_mode else self._LIVE_API

    def verify_signature(self, data: Dict[str, Any], signature: str) -> bool:
        """
        Verifies the signature of the webhook request.

        Parameters
        ----------
        data : Dict[str, Any]
            The webhook event data containing transmission details
        signature : str
            The signature to verify

        Returns
        -------
        bool
            True if the signature is valid, False otherwise
        """
        try:
            # Extract necessary components from data
            transmission_id = data["transmissionId"]
            timestamp = data["timestamp"]
            webhook_id = data["webhookId"]
            event_body = data["eventBody"]
            cert_url = data["certUrl"]
            auth_algo = data["authAlgo"]

            # Ensure the webhook_id matches the expected one
            if webhook_id != self._webhook_id:
                raise ValueError("Webhook ID does not match the expected value")

            # Get the certificate (from cache or fetch new)
            cert = self._get_certificate(cert_url)

            # Construct the expected message
            expected_message = f"{transmission_id}|{timestamp}|{webhook_id}|{event_body}"

            # Decode the actual signature from base64
            decoded_signature = base64.b64decode(signature)

            # Verify using appropriate algorithm
            if auth_algo == "SHA256withRSA":
                hash_alg = hashes.SHA256()
            else:
                raise ValueError(f"Unsupported auth_algo: {auth_algo}")

            # Verify the signature
            public_key = cert.public_key()
            if not isinstance(public_key, rsa.RSAPublicKey):
                raise TypeError("Unsupported public key type for signature verification")

            public_key.verify(
                decoded_signature,
                expected_message.encode("utf-8"),
                padding.PKCS1v15(),
                hash_alg
            )

            return True

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
        signature = header.get("PAYPAL-TRANSMISSION-SIG")
        if not signature:
            raise ValueError("Missing PayPal signature in headers")
        if not isinstance(signature, str):
            raise ValueError("Invalid PayPal signature format")
        return signature

    def verify_webhook_id(self, webhook_id: str) -> bool:
        """
        Verifies a webhook ID with PayPal's API.

        Parameters
        ----------
        webhook_id : str
            The webhook ID to verify

        Returns
        -------
        bool
            True if the webhook ID is valid, False otherwise
        """
        try:
            headers = self._get_auth_headers()
            response = requests.get(
                f"{self.api_base_url}/notifications/webhooks/{webhook_id}",
                headers=headers
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Webhook ID verification failed: {str(e)}")
            return False

    def _get_certificate(self, cert_url: str) -> x509.Certificate:
        """
        Gets the certificate from cache or fetches it from PayPal.

        Parameters
        ----------
        cert_url : str
            The URL of the certificate

        Returns
        -------
        x509.Certificate
            The PayPal certificate

        Raises
        ------
        ValueError
            If certificate fetching fails
        """
        if cert_url in self._CERT_CACHE:
            return self._CERT_CACHE[cert_url]

        try:
            response = requests.get(cert_url)
            response.raise_for_status()
            cert_data = response.content
            cert = x509.load_pem_x509_certificate(cert_data, default_backend())
            
            # Cache the certificate
            self._CERT_CACHE[cert_url] = cert
            
            return cert
        except Exception as e:
            raise ValueError(f"Failed to fetch PayPal certificate: {str(e)}")

    def _get_auth_headers(self) -> Dict[str, str]:
        """
        Gets the authentication headers for PayPal API requests.

        Returns
        -------
        Dict[str, str]
            The authentication headers
        """
        return {
            "Authorization": f"Bearer {self._secret}",
            "Content-Type": "application/json"
        }
