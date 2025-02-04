# TypeScript Payment API

A flexible payment API built with TypeScript that supports multiple payment providers including PayPal, Stripe, Coinbase, Google Pay, and Apple Pay.

## Installation

```bash
npm install @dclmonster/ts-payment-api
# or
yarn add @dclmonster/ts-payment-api
```

## Quick Start

```typescript
import { createPaymentServer } from 'extendable-payment-api';
import { Config } from 'extendable-payment-api/config';

const app = createPaymentServer();
app.listen(3000, () => {
  console.log('Payment server running on port 3000');
});
```

## Configuration

### Environment Variables

```env
# Required Core Settings
PORT=3000
MONGODB_URI=mongodb://localhost:27017/payment_db
JWT_SECRET=your-jwt-secret
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

- TypeScript support with full type definitions
- Multiple payment provider support
- Webhook handling for payment notifications
- Transaction status tracking
- Payment verification
- Error handling and logging
- Rate limiting
- JWT authentication

## API Endpoints

### Payment Creation

```typescript
interface PaymentRequest {
  provider: 'paypal' | 'coinbase' | 'google' | 'apple';
  amount: number;
  currency: string;
  description: string;
}

// Example usage
POST /api/v1/payments
Content-Type: application/json
Authorization: Bearer your-jwt-token

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
npm test -- --testPathPattern=/__tests__/unit/

# Run with coverage
npm test -- --testPathPattern=/__tests__/unit/ --coverage
```

### Integration Tests
```bash
# Run integration tests
npm test -- --testPathPattern=/__tests__/integration/

# Run specific provider tests
npm test -- --testPathPattern=/__tests__/integration/paypal
```

### Regression Tests
```bash
# Run regression tests
npm test -- --testPathPattern=/__tests__/regression/

# Run specific regression suite
npm test -- --testPathPattern=/__tests__/regression/api-compatibility
```

### Performance Tests
```bash
# Run performance benchmarks
npm test -- --testPathPattern=/__tests__/performance/ --config=jest.bench.config.js

# Compare with previous run
npm run benchmark:compare
```

## Development

### Setup Development Environment
```bash
# Clone the repository
git clone https://github.com/DclMonster/ExtendablePaymentApi.git

# Install dependencies
npm install

# Install pre-commit hooks
pre-commit install
```

### Code Quality Tools
```bash
# Format code
npm run format

# Lint code
npm run lint

# Type check
npm run type-check

# Run all pre-commit hooks
pre-commit run --all-files
```

### Performance Monitoring
- Benchmark results stored in `benchmark-results.json`
- Performance regression threshold: 10%
- Benchmark comparison in CI/CD pipeline
- Load testing scenarios in `__tests__/performance/`
- Metrics tracked: mean, median, stddev

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

The API uses standard HTTP status codes and returns typed error responses:

```typescript
interface ErrorResponse {
  error: string;
  message: string;
  status: number;
}

// Example
{
    "error": "InvalidPaymentProvider",
    "message": "Unsupported payment provider",
    "status": 400
}
```

## Type Documentation

Full TypeScript documentation is available in the `docs` folder or can be generated using:

```bash
npm run docs
```

## Contributing

1. Fork the repository
2. Create your feature branch
3. Run tests and benchmarks
4. Ensure code quality with pre-commit hooks
5. Submit a pull request

## Documentation

- Full API documentation at `/docs`
- Performance benchmarks at `/docs/benchmarks`
- Integration guides at `/docs/integration`
- Type definitions in `dist/types`

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

# Create/update npm config
echo "@exodus:registry=https://npm.pkg.github.com" >> ~/.npmrc
echo "//npm.pkg.github.com/:_authToken=${GITHUB_TOKEN}" >> ~/.npmrc
```

### Installing the Package

```bash
# Install the package
npm install @dclmonster/ts-payment-api

# Install as a development dependency
npm install --save-dev @dclmonster/ts-payment-api
```

### Publishing Updates

```bash
# Build and publish
npm run build
npm publish
```

## Development Setup

1. Clone the repository
2. Install dependencies:
```bash
npm install
``` 