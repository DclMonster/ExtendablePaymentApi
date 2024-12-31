import jwt
import os

class GoogleVerifier:
    """
    Verifier class for Google webhook signatures.
    """

    def __init__(self):
        """
        Initializes the verifier with the public key from environment variables.
        """
        self.public_key = os.getenv('GOOGLE_PUBLIC_KEY')
        if not self.public_key:
            raise ValueError("Google public key not set in environment variables.")

    def verify_signature(self, jwt_token: str) -> bool:
        """
        Verifies the signature of the webhook request.

        Parameters
        ----------
        jwt_token : str
            The JWT token from the event data.

        Returns
        -------
        bool
            True if the signature is valid, False otherwise.
        """
        try:
            decoded = jwt.decode(jwt_token, self.public_key, algorithms=['RS256'])
            return True
        except jwt.exceptions.InvalidSignatureError:
            return False
        except jwt.exceptions.DecodeError:
            return False 