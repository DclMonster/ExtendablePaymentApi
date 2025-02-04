# Python Payment API

A flexible payment API that supports multiple payment providers including PayPal, Stripe, Coinbase, Google Pay, and Apple Pay.

## Installation

```bash
pip install @dclmonster/py-payment-api
```

## Quick Start

```python
from py_payment_api import create_app
from py_payment_api.config import Config

app = create_app()
app.run()
```

## Configuration

### Environment Variables

```env
# Required Core Settings
MONGODB_URI=mongodb://localhost:27017/payment_db
JWT_SECRET_KEY=your-secret-key
API_KEY=your-api-key

# PayPal Configuration
PAYPAL_CLIENT_ID=your-paypal-client-id
PAYPAL_CLIENT_SECRET=your-paypal-client-secret
PAYPAL_WEBHOOK_ID=your-paypal-webhook-id

# Coinbase Configuration
COINBASE_API_KEY=your-coinbase-api-key
COINBASE_WEBHOOK_SECRET=your-coinbase-webhook-secret

# Google Pay Configuration
GOOGLE_PAY_MERCHANT_ID=your-merchant-id
GOOGLE_PAY_MERCHANT_NAME=your-merchant-name

# Apple Pay Configuration
APPLE_PAY_MERCHANT_ID=your-merchant-id
APPLE_PAY_CERTIFICATE_PATH=/path/to/certificate.pem
```

## Features

- Multiple payment provider support
- Webhook handling for payment notifications
- Transaction status tracking
- Payment verification
- Error handling and logging
- Rate limiting
- API key authentication

## API Endpoints

### Payment Creation

```bash
POST /api/v1/payments
Content-Type: application/json
Authorization: Bearer your-api-key

{
    "provider": "paypal",
    "amount": 100.00,
    "currency": "USD",
    "description": "Test payment"
}
```

### Webhook Endpoints

- PayPal: `/api/v1/webhooks/paypal`
- Coinbase: `/api/v1/webhooks/coinbase`
- Google Pay: `/api/v1/webhooks/google`
- Apple Pay: `/api/v1/webhooks/apple`

## Testing

The project includes four types of tests:

### Unit Tests
```bash
# Run unit tests
pytest tests/unit -v -m "unit"

# Run with coverage
pytest tests/unit -v -m "unit" --cov=py_payment_api
```

### Integration Tests
```bash
# Run integration tests
pytest tests/integration -v -m "integration"

# Run specific provider tests
pytest tests/integration/test_paypal.py -v
```

### Regression Tests
```bash
# Run regression tests
pytest tests/regression -v -m "regression"

# Run specific regression suite
pytest tests/regression/test_api_compatibility.py -v
```

### Performance Tests
```bash
# Run performance benchmarks
pytest tests/performance -v -m "performance" --benchmark-only

# Compare with previous run
pytest tests/performance -v --benchmark-compare
```

## Development

### Setup Development Environment
```bash
# Clone the repository
git clone https://github.com/DclMonster/ExtendablePaymentApi.git

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Install pre-commit hooks
pre-commit install
```

### Code Quality Tools
```bash
# Format code
black .

# Sort imports
isort .

# Run linting
flake8
pylint **/*.py

# Type checking
mypy .

# Run all pre-commit hooks
pre-commit run --all-files
```

### Performance Monitoring
- Benchmark results are stored in `.benchmarks/`
- Performance regression threshold: 10%
- Benchmark comparison available in CI/CD pipeline
- Load testing scenarios in `tests/performance/`

## Provider Setup

### PayPal Setup
1. Create a PayPal Developer account
2. Get your client ID and secret
3. Set up webhook URL in PayPal Developer Dashboard
4. Configure environment variables

### Coinbase Setup
1. Create a Coinbase Commerce account
2. Generate API keys
3. Configure webhook endpoint
4. Set environment variables

### Google Pay Setup
1. Register in Google Pay Business Console
2. Get merchant ID
3. Configure payment methods
4. Set environment variables

### Apple Pay Setup
1. Register in Apple Developer Program
2. Create merchant ID
3. Generate and upload certificates
4. Set environment variables

## Error Handling

The API uses standard HTTP status codes and returns detailed error messages:

```json
{
    "error": "InvalidPaymentProvider",
    "message": "Unsupported payment provider",
    "status": 400
}
```

## Contributing

1. Fork the repository
2. Create your feature branch
3. Run tests and benchmarks
4. Ensure code quality with pre-commit hooks
5. Submit a pull request

## Documentation

- Full API documentation available at `/docs`
- Performance benchmarks at `/docs/benchmarks`
- Integration guides at `/docs/integration`
- TypeScript definitions in `py.typed`

## License

MIT License - see LICENSE file for details

## Package Installation

This package is available on GitHub Packages.

### Authentication Setup

1. Create a GitHub Personal Access Token (PAT) with `read:packages` scope (and `write:packages` if you need to publish).

2. Set up authentication:
```bash
# Set environment variable for PAT
export GITHUB_TOKEN=your_github_pat_here

# Create/update pip config
cat << EOF > ~/.pip/pip.conf
[global]
extra-index-url=https://download-packages.github.com/exodus/ExtendablePaymentApi/simple/
trusted-host=download-packages.github.com
EOF

# Create/update PyPI config for publishing
cat << EOF > ~/.pypirc
[distutils]
index-servers = github

[github]
repository = https://upload-wheels.github.com/exodus/ExtendablePaymentApi
username = __token__
password = ${GITHUB_TOKEN}
EOF
```

### Installing the Package

```bash
# Install the package
pip install @dclmonster/py-payment-api

# Install with development dependencies
pip install @dclmonster/py-payment-api[dev]
```

### Publishing Updates

```bash
# Build and publish
python -m build
twine upload -r github dist/*
```

### Development Setup

1. Clone the repository
```bash
git clone https://github.com/DclMonster/ExtendablePaymentApi.git
```

2. Install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e .[dev]
``` 