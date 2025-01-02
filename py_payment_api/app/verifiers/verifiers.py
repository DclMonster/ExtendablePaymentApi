from .apple_verifier import AppleVerifier
from .google_verifier import GoogleVerifier
from .coinbase_verifier import CoinbaseVerifier
from .paypal_verifier import PayPalVerifier
from .coinsub_verifier import CoinsubVerifier

# Initialize verifiers
apple_verifier = AppleVerifier()
google_verifier = GoogleVerifier()
coinbase_verifier = CoinbaseVerifier() 
paypal_verifier = PayPalVerifier()
coinsub_verifier = CoinsubVerifier()