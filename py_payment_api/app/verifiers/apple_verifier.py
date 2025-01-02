import jwt
import os

class AppleVerifier:
    """
    Verifier class for Apple webhook signatures.
    """

    def __init__(self):
        """
        Initializes the verifier with the public key from environment variables.
        """
        self.public_key = os.getenv('APPLE_PUBLIC_KEY')
        if not self.public_key:
            raise ValueError("Apple public key not set in environment variables.")

    def verify_signature(self, jws: str) -> bool:
        """
        Verifies the signature of the webhook request.

        Parameters
        ----------
        jws : str
            The signed payload from the event data.

        Returns
        -------
        bool
            True if the signature is valid, False otherwise.
        """
        try:
            decoded = jwt.decode(jws, self.public_key, algorithms=['ES256'])
            return True
        except jwt.exceptions.InvalidSignatureError:
            return False
        except jwt.exceptions.DecodeError:
            return False 