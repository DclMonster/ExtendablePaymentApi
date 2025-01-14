import hmac
import hashlib
import os
from .abstract.signature_verifier import SignatureVerifier

class CoinbaseVerifier(SignatureVerifier):
    """
    Verifier class for Coinbase webhook signatures.
    """

    def __init__(self):
        """
        Initializes the verifier with the secret from environment variables.
        """
        super('COINBASE_WEBHOOK_SECRET')

    def verify_signature(self, data: str, signature: str) -> bool:
        """
        Verifies the signature of the webhook request.

        Parameters
        ----------
        data : str
            The raw request data.
        signature : str
            The signature from the request headers.

        Returns
        -------
        bool
            True if the signature is valid, False otherwise.
        """
        computed_signature = hmac.new(
            key=self._secret.encode(),
            msg=data.encode(),
            digestmod=hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(computed_signature, signature) 

    def get_signature_from_header(self, header) -> str:
        return header.get('CB-SIGNATURE', '') 