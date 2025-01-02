import hmac
import hashlib
import os

class CoinbaseVerifier:
    """
    Verifier class for Coinbase webhook signatures.
    """

    def __init__(self):
        """
        Initializes the verifier with the secret from environment variables.
        """
        self.secret = os.getenv('COINBASE_WEBHOOK_SECRET')
        if not self.secret:
            raise ValueError("Coinbase webhook secret not set in environment variables.")

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
            key=self.secret.encode(),
            msg=data.encode(),
            digestmod=hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(computed_signature, signature) 