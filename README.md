## Key Components

- **Resources**: Handle incoming webhook requests and process them.
  - `CoinbaseWebhook`: Manages Coinbase webhook events.
  - `AppleWebhook`: Manages Apple webhook events.
  - `GoogleWebhook`: Manages Google webhook events.

- **Services**: Provides business logic and action management.
  - `PaymentService`: Manages registration and execution of actions for different payment providers.

- **Verifiers**: Ensure the authenticity of webhook requests.
  - `CoinbaseVerifier`: Verifies Coinbase webhook signatures.
  - `AppleVerifier`: Verifies Apple webhook signatures.
  - `GoogleVerifier`: Verifies Google webhook signatures.

## Setup

### Prerequisites

- Python 3.7+
- Flask
- Flask-RESTful
- PyJWT
- pytest
- python-dotenv (for local development)

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/payment-api.git
   cd payment-api
   ```

2. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:

   Create a `.env` file in the root directory and add the following:

   ```plaintext
   COINBASE_WEBHOOK_SECRET=your_coinbase_secret
   APPLE_PUBLIC_KEY=your_apple_public_key
   GOOGLE_PUBLIC_KEY=your_google_public_key
   ```

### Running the Application

To start the application, run:

```

Ensure all required environment variables are set before starting the application.

## Testing

Run the tests using `pytest`:

```

## Usage

- **Webhook Endpoints**:
  - `/webhook/coinbase`: Endpoint for Coinbase webhooks.
  - `/webhook/apple`: Endpoint for Apple webhooks.
  - `/webhook/google`: Endpoint for Google webhooks.

- **Action Registration**: Use the `PaymentService` to register actions that should be executed when a webhook event is received.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.