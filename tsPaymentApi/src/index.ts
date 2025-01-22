import express from 'express';
import dotenv from 'dotenv';
import { PaymentProvider } from './services/PaymentProvider';
import { ItemType } from './services/ItemType';
import { configureWebhook, configureCreditor } from './config/config';
import { initializeServices } from './services';

// Load environment variables
dotenv.config();

// Create Express app
const app = express();

// Middleware
app.use(express.json());

// Initialize services (this should be replaced with actual service implementations)
initializeServices({
    getPurchaseType: () => ItemType.UNKNOWN,
    handleOneTimePayment: async () => {},
    handleSubscription: async () => {}
});

// Configure routes
const enabledProviders = [
    PaymentProvider.PAYPAL,
    PaymentProvider.APPLE,
    PaymentProvider.GOOGLE,
    PaymentProvider.COINBASE,
    PaymentProvider.COINSUB
];

configureWebhook(app, enabledProviders, {
    forwardEvent: async () => {}
});
configureCreditor(app);

// Start server
const port = process.env.PORT || 3000;
app.listen(port, () => {
    console.log(`Server is running on port ${port}`);
});