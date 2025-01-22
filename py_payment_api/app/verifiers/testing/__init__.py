"""Testing package for verifiers."""
import os

# Set mock secrets for testing
os.environ['APPLE_PUBLIC_KEY'] = 'test_apple_key'
os.environ['GOOGLE_PUBLIC_KEY'] = 'test_google_key'
os.environ['COINBASE_SECRET'] = 'test_coinbase_secret'
os.environ['PAYPAL_SECRET'] = 'test_paypal_secret'
os.environ['PAYPAL_WEBHOOK_ID'] = 'WH-1234567890'
os.environ['COINSUB_SECRET'] = 'test_coinsub_secret' 