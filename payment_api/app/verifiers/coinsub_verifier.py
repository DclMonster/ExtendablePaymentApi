import hmac
import hashlib
import os

class CoinsubVerifier:
    def __init__(self):
        secret : str | None = os.getenv('COINSUB_SECRET')
        if not secret:
            raise ValueError("COINSUB_SECRET environment variable must be set")
        self.__secret = secret

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
        computed_signature = hmac.new(self.__secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
        return hmac.compare_digest(computed_signature, actual_signature) 