import express from 'express';
import dotenv from 'dotenv';
import { PaymentProvider } from './services/PaymentProvider';
import { ItemType } from './services/ItemType';
import { configureWebhook, configureCreditor } from './config/config';
import { initializeServices } from './services';
import cors from 'cors';
import helmet from 'helmet';
import { PayPalWebhook } from './resources/webhook/PayPalWebhook';
import { CoinbaseWebhook } from './resources/webhook/CoinbaseWebhook';
import { WebSocketForwarder } from './services/forwarder/WebSocketForwarder';
import { Logger } from './utils/Logger';
import { WebhookError } from './errors/WebhookError';

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

interface WebhookConfig {
    creditorId: string;
    creditorName: string;
    creditorType: 'MERCHANT' | 'PLATFORM';
    webhookUrl: string;
    supportedProviders: Array<'PAYPAL' | 'COINBASE'>;
    metadata?: Record<string, any>;
}

export function configureWebhook(config: WebhookConfig): express.Application {
    const app = express();

    // Security middleware
    app.use(helmet());
    app.use(cors());
    app.use(express.json());

    // Initialize forwarder
    const forwarder = new WebSocketForwarder(config.webhookUrl);

    // Initialize webhook handlers
    const webhooks = new Map();
    if (config.supportedProviders.includes('PAYPAL')) {
        webhooks.set('paypal', new PayPalWebhook(forwarder));
    }
    if (config.supportedProviders.includes('COINBASE')) {
        webhooks.set('coinbase', new CoinbaseWebhook(forwarder));
    }

    // Webhook endpoint
    app.post('/webhook/:provider', async (req, res) => {
        const provider = req.params.provider.toLowerCase();
        const webhook = webhooks.get(provider);

        if (!webhook) {
            return res.status(400).json({
                error: `Unsupported payment provider: ${provider}`
            });
        }

        try {
            // Add creditor info to the request
            req.body.creditor = {
                id: config.creditorId,
                name: config.creditorName,
                type: config.creditorType,
                metadata: config.metadata
            };

            // Verify webhook signature
            const signature = webhook.verifier.getSignatureFromHeader(req.headers);
            const isValid = webhook.verifier.verifySignature(req.body, signature);

            if (!isValid) {
                throw new WebhookError('Invalid webhook signature');
            }

            // Process webhook event
            await webhook.processEvent(JSON.stringify(req.body));

            res.status(200).json({ status: 'success' });
        } catch (error) {
            Logger.error(`Webhook error (${provider}):`, error);
            
            if (error instanceof WebhookError) {
                return res.status(400).json({
                    error: error.message
                });
            }

            res.status(500).json({
                error: 'Internal server error processing webhook'
            });
        }
    });

    // Health check endpoint
    app.get('/health', (_, res) => {
        res.status(200).json({
            status: 'healthy',
            creditor: {
                id: config.creditorId,
                name: config.creditorName,
                type: config.creditorType,
                providers: config.supportedProviders
            }
        });
    });

    return app;
}

// Export webhook handlers for direct usage
export { PayPalWebhook, CoinbaseWebhook };