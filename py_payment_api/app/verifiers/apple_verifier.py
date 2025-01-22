import jwt
import os
from .abstract.signature_verifier import SignatureVerifier
from typing import Dict, Any, cast

class AppleVerifier(SignatureVerifier):
    """
    Verifier class for Apple webhook signatures.
    """

    def __init__(self) -> None:
        """
        Initializes the verifier with the public key from environment variables.
        """
        super().__init__('APPLE_PUBLIC_KEY')

    def verify_signature(self, data: Dict[str, Any], signature: str) -> bool:
        """
        Verifies the signature of the webhook request.

        Parameters
        ----------
        data : Dict[str, Any]
            The signed payload from the event data.
        signature : str
            The signature to verify.

        Returns
        -------
        bool
            True if the signature is valid, False otherwise.
        """
        try:
            jwt.decode(signature, self._secret, algorithms=['ES256'], audience=data['transactionId'])
            return True
        except jwt.exceptions.InvalidSignatureError:
            return False
        except jwt.exceptions.DecodeError:
            return False

    def get_signature_from_header(self, header: Dict[str, Any]) -> str:
        """
        Extracts the signature from the header.

        Parameters
        ----------
        header : Any
            The header containing the signature.

        Returns
        -------
        str
            The extracted signature.
        """
        signature = header.get('x-apple-signature', '') 
        if not isinstance(signature, str):
            raise ValueError("Signature is not a string")
        return signature