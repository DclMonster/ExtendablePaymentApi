import jwt
import os
from typing import Any, Dict, Optional
from .abstract.signature_verifier import SignatureVerifier

class GoogleVerifier(SignatureVerifier):
    """
    Verifier class for Google webhook signatures.
    """
    _secret: str

    def __init__(self) -> None:
        """
        Initializes the verifier with the public key from environment variables.
        
        Raises
        ------
        ValueError
            If the required environment variable is not set.
        """
        super().__init__('GOOGLE_PUBLIC_KEY')

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
            jwt.decode(signature, self._secret, algorithms=['RS256'])
            return True
        except (jwt.exceptions.InvalidSignatureError, jwt.exceptions.DecodeError):
            return False

    def get_signature_from_header(self, header: Dict[str, str]) -> str:
        """
        Extracts the signature from the header.

        Parameters
        ----------
        header : Dict[str, Any]
            The header containing the signature.

        Returns
        -------
        Optional[str]
            The extracted signature, or None if not found.
        """
        return header.get('Signature','') 