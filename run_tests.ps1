$env:TESTING='true'
$env:APPLE_PUBLIC_KEY='test_apple_key'
$env:GOOGLE_PUBLIC_KEY='test_google_key'
$env:COINBASE_SECRET='test_coinbase_secret'
$env:PAYPAL_SECRET='test_paypal_secret'
$env:PAYPAL_WEBHOOK_ID='WH-1234567890'
$env:COINSUB_SECRET='test_coinsub_secret'
python -m pytest -v
