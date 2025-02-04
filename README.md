# Extendable Payment API

A flexible payment API supporting multiple payment providers, implemented in both Python and TypeScript.

## Project Structure

```
ExtendablePaymentApi/
├── py_payment_api/         # Python implementation
│   ├── app/               # Core Python application code
│   ├── tests/             # Python tests (unit, integration, regression)
│   ├── docs/              # Python documentation
│   ├── requirements.txt   # Python dependencies
│   ├── setup.py          # Python package configuration
│   ├── pyproject.toml    # Python build system configuration
│   ├── pytest.ini        # Python test configuration
│   └── README.md         # Python-specific documentation
│
├── tsPaymentApi/          # TypeScript implementation
│   ├── src/              # Core TypeScript application code
│   ├── tests/            # TypeScript tests (unit, integration, regression)
│   ├── docs/             # TypeScript documentation
│   ├── package.json      # TypeScript dependencies and scripts
│   ├── tsconfig.json     # TypeScript configuration
│   ├── jest.config.js    # Jest test configuration
│   └── README.md         # TypeScript-specific documentation
│
├── .github/              # GitHub Actions workflows
│   └── workflows/        # CI/CD pipeline configurations
│
└── README.md            # Root project documentation
```

## Getting Started

This project contains two independent implementations of the same API:

### Python Implementation
```bash
cd py_payment_api
make install  # Install dependencies
make dev      # Start development server
```

### TypeScript Implementation
```bash
cd tsPaymentApi
npm install   # Install dependencies
npm run dev   # Start development server
```

## Development

Each implementation has its own development workflow and tools. Please refer to the respective README files in each directory:

- [Python Implementation](py_payment_api/README.md)
- [TypeScript Implementation](tsPaymentApi/README.md)

## Testing

Both implementations include comprehensive test suites:

### Python Tests
```bash
cd py_payment_api
make test              # Run all tests
make test-unit        # Run unit tests
make test-integration # Run integration tests
make test-regression  # Run regression tests
make test-performance # Run performance tests
```

### TypeScript Tests
```bash
cd tsPaymentApi
npm test              # Run all tests
npm run test:unit     # Run unit tests
npm run test:integration # Run integration tests
npm run test:regression # Run regression tests
npm run test:performance # Run performance tests
```

## Documentation

Each implementation maintains its own documentation:

### Python Documentation
```bash
cd py_payment_api
make docs      # Build documentation
make docs-serve # Serve documentation locally
```

### TypeScript Documentation
```bash
cd tsPaymentApi
npm run docs   # Build documentation
npm run docs:serve # Serve documentation locally
```

## Contributing

Please read the contribution guidelines in each implementation's directory before submitting pull requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Supported Payment Providers

### WooCommerce Integration

The payment API supports WooCommerce webhooks for handling orders and subscriptions. 

#### Configuration

Set the following environment variables:
```
WOOCOMMERCE_CONSUMER_KEY=your_consumer_key
WOOCOMMERCE_CONSUMER_SECRET=your_consumer_secret
WOOCOMMERCE_WEBHOOK_SECRET=your_webhook_secret
WOOCOMMERCE_API_URL=your_store_url
```

#### Setup Steps:

1. In WooCommerce admin panel:
   - Go to WooCommerce > Settings > Advanced > REST API
   - Click "Add Key" to create new API credentials
   - Set permissions to "Read/Write"
   - Copy the Consumer Key and Consumer Secret

2. Configure webhooks:
   - Go to WooCommerce > Settings > Advanced > Webhooks
   - Create webhooks for:
     - Order created/updated
     - Subscription created/renewed
     - Subscription cancelled
   - Set delivery URL to your API endpoint
   - Copy the Webhook Secret

3. Update environment variables with the copied values

#### Supported Events:
- `order.created`: New order created
- `order.updated`: Order status updated
- `subscription.created`: New subscription created
- `subscription.renewed`: Subscription renewed
- `subscription.cancelled`: Subscription cancelled

#### Testing:
Use WooCommerce webhook delivery system:
1. Go to WooCommerce > Settings > Advanced > Webhooks
2. Select a webhook
3. Click "Send test" to deliver a test payload