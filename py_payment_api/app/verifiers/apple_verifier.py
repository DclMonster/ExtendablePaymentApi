import jwt
import os
from .abstract.signature_verifier import SignatureVerifier

class AppleVerifier(SignatureVerifier):
    """
    Verifier class for Apple webhook signatures.
    """

    def __init__(self):
        """
        Initializes the verifier with the public key from environment variables.
        """
        super('APPLE_PUBLIC_KEY')

    def verify_signature(self, data: str, signature: str) -> bool:
        """
        Verifies the signature of the webhook request.

        Parameters
        ----------
        data : str
            The signed payload from the event data.
        signature : str
            The signature to verify.

        Returns
        -------
        bool
            True if the signature is valid, False otherwise.
        """
        try:
            decoded = jwt.decode(signature, self._secret, algorithms=['ES256'])
            return True
        except jwt.exceptions.InvalidSignatureError:
            return False
        except jwt.exceptions.DecodeError:
            return False

    def get_signature_from_header(self, header) -> str:
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
        return header.get('Signature', '') 