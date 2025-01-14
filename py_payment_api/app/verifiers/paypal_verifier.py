import os
import requests
import hashlib
import base64
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from .abstract.signature_verifier import SignatureVerifier

class PayPalVerifier(SignatureVerifier):
    def __init__(self):
        super('PAYPAL_SECRET')
        self.__webhook_id = os.getenv('PAYPAL_WEBHOOK_ID')  # Ensure you set this environment variable

    def verify_signature(self, data: str, signature: str) -> bool:
        try:
            # Extract necessary components from data
            transmission_id, timestamp, webhook_id, event_body, cert_url, auth_algo = data.split('|')

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
            decoded_signature = base64.b64decode(signature)

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

    def get_signature_from_header(self, header) -> str:
        return header.get('PAYPAL-AUTH-ALGO', '')

        