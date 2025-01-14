import hmac
import hashlib
import os
from .abstract.signature_verifier import SignatureVerifier

class CoinsubVerifier(SignatureVerifier):
    def __init__(self):
        super('COINSUB_SECRET')

    def verify_signature(self, payload: str, actual_signature: str | None) -> bool:
        """
        Verifies the CoinSub webhook signature.

        Parameters
        ----------
        payload : str
            The payload of the webhook event.
        actual_signature : str
            The actual signature to verify.

        Returns
        -------
        bool
            True if the signature is valid, False otherwise.
        """
        if not actual_signature:
            raise ValueError("Signature not provided")
        computed_signature = hmac.new(self._secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
        return hmac.compare_digest(computed_signature, actual_signature) 

    def get_signature_from_header(self, header) -> str:
        return header.get('COINSUB-SIGNATURE', '') 