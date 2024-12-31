import os
import requests
import hashlib
import base64
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
class PayPalVerifier:
    def __init__(self):
        secret = os.getenv('PAYPAL_SECRET')
        if secret is None:
            raise ValueError("PAYPAL_SECRET environment variable must be set")
        self.__secret = secret
        self.__webhook_id = os.getenv('PAYPAL_WEBHOOK_ID')  # Ensure you set this environment variable

    def verify_signature(self, transmission_id: str, timestamp: str, webhook_id: str, event_body: str, cert_url: str, actual_signature: str, auth_algo: str) -> bool:
        """
        Verifies the PayPal webhook signature.

        Parameters
        ----------
        transmission_id : str
            The PayPal transmission ID.
        timestamp : str
            The timestamp of the transmission.
        webhook_id : str
            The ID of the webhook.
        event_body : str
            The body of the webhook event.
        cert_url : str
            The certificate URL.
        actual_signature : str
            The actual signature to verify.
        auth_algo : str
            The algorithm used for the signature.

        Returns
        -------
        bool
            True if the signature is valid, False otherwise.
        """
        try:
            # Ensure the webhook_id matches the expected one
            if webhook_id != self.__webhook_id:
                raise ValueError("Webhook ID does not match the expected value.")

            # Step 1: Fetch PayPal's public certificate
            response = requests.get(cert_url)
            response.raise_for_status()
            cert_data = response.content
            cert = x509.load_pem_x509_certificate(cert_data, default_backend())

            # Step 2: Construct the expected message
            expected_message = f"{transmission_id}|{timestamp}|{webhook_id}|{event_body}"

            # Step 3: Decode the actual signature from base64
            decoded_signature = base64.b64decode(actual_signature)

            # Step 4: Determine the hash algorithm
            if auth_algo == "SHA256withRSA":
                hash_alg = hashes.SHA256()
            else:
                raise ValueError(f"Unsupported auth_algo: {auth_algo}")

            # Step 5: Verify the signature
            public_key = cert.public_key()
            if isinstance(public_key, rsa.RSAPublicKey):
                public_key.verify(
                    decoded_signature,
                    expected_message.encode('utf-8'),
                    padding.PKCS1v15(),
                    hash_alg,
                )
            else:
                raise TypeError("Unsupported public key type for signature verification.")

            # If no exception was raised, the signature is valid
            return True

        except Exception as e:
            # Log the exception details for debugging
            print(f"Signature verification failed: {str(e)}")
            return False

        