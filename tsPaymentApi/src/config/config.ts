import express, { Express } from 'express';
import { PaymentProvider } from '../services/PaymentProvider';
import { Forwarder } from '../services/forwarder/abstract/Forwarder';
import { CoinbaseWebhook, AppleWebhook, GoogleWebhook, PaypalWebhook, CoinSubWebhook } from '../resources/webhook';
import { CreditPurchase } from '../resources/creditor';
import dotenv from 'dotenv';

export const configureWebhook = (
    app: Express,
    enabledProviders: PaymentProvider[],
    forwarder: Forwarder
): void => {
    // Load environment variables
    dotenv.config();

    // Conditionally register the webhook resources
    if (enabledProviders.includes(PaymentProvider.COINBASE)) {
        app.use('/webhook/coinbase', new CoinbaseWebhook(forwarder).router);
    }
    if (enabledProviders.includes(PaymentProvider.APPLE)) {
        app.use('/webhook/apple', new AppleWebhook(forwarder).router);
    }
    if (enabledProviders.includes(PaymentProvider.GOOGLE)) {
        app.use('/webhook/google', new GoogleWebhook(forwarder).router);
    }
    if (enabledProviders.includes(PaymentProvider.PAYPAL)) {
        app.use('/webhook/paypal', new PaypalWebhook(forwarder).router);
    }
    if (enabledProviders.includes(PaymentProvider.COINSUB)) {
        app.use('/webhook/coinsub', new CoinSubWebhook(forwarder).router);
    }
};

export const configureCreditor = (app: Express): void => {
    app.use('/creditor/transaction', new CreditPurchase().router);
}; 