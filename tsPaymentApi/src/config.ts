import { Express } from 'express';
import { PaymentProvider } from './services/store/enum/PaymentProvider';
import { Forwarder } from './services/forwarder/abstract/Forwarder';
import dotenv from 'dotenv';

// Import webhook handlers
import { CoinbaseWebhook } from './resources/webhook/CoinbaseWebhook';
import { AppleWebhook } from './resources/webhook/AppleWebhook';
import { GoogleWebhook } from './resources/webhook/GoogleWebhook';
import { PaypalWebhook } from './resources/webhook/PaypalWebhook';
import { CoinSubWebhook } from './resources/webhook/CoinSubWebhook';
import { CreditPurchase } from './resources/creditor/creditPurchase';

/**
 * Configure webhook endpoints for the given Express application.
 * 
 * @param app - The Express application to configure
 * @param enabledProviders - List of enabled payment providers
 * @param forwarder - The forwarder instance to use for webhook events
 */
export function configureWebhook(app: Express, enabledProviders: PaymentProvider[], forwarder: Forwarder): void {
    // Load environment variables
    dotenv.config();

    // Create webhook instances
    const webhooks = {
        [PaymentProvider.COINBASE]: new CoinbaseWebhook(forwarder),
        [PaymentProvider.APPLE]: new AppleWebhook(forwarder),
        [PaymentProvider.GOOGLE]: new GoogleWebhook(forwarder),
        [PaymentProvider.PAYPAL]: new PaypalWebhook(forwarder),
        [PaymentProvider.COINSUB]: new CoinSubWebhook(forwarder)
    };

    // Conditionally register the webhook resources
    if (enabledProviders.includes(PaymentProvider.COINBASE)) {
        app.use('/webhook/coinbase', webhooks[PaymentProvider.COINBASE].router);
    }
    if (enabledProviders.includes(PaymentProvider.APPLE)) {
        app.use('/webhook/apple', webhooks[PaymentProvider.APPLE].router);
    }
    if (enabledProviders.includes(PaymentProvider.GOOGLE)) {
        app.use('/webhook/google', webhooks[PaymentProvider.GOOGLE].router);
    }
    if (enabledProviders.includes(PaymentProvider.PAYPAL)) {
        app.use('/webhook/paypal', webhooks[PaymentProvider.PAYPAL].router);
    }
    if (enabledProviders.includes(PaymentProvider.COINSUB)) {
        app.use('/webhook/coinsub', webhooks[PaymentProvider.COINSUB].router);
    }
}

/**
 * Configure creditor endpoint for the given Express application.
 * 
 * @param app - The Express application to configure
 */
export function configureCreditor(app: Express): void {
    const creditPurchase = new CreditPurchase();
    app.use('/creditor/transaction', creditPurchase.router);
} 