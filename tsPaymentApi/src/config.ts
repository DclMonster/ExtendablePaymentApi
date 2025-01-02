import express, { Application } from 'express';
import { Api } from 'express-restful-api';
import * as resources from './resources/index';
import dotenv from 'dotenv';

export function configureWebhook(app: Application): void {
    dotenv.config();

    const api = new Api(app);

    api.addResource(resources.CoinbaseWebhook, '/webhook/coinbase');
    api.addResource(resources.AppleWebhook, '/webhook/apple');
    api.addResource(resources.GoogleWebhook, '/webhook/google');
    api.addResource(resources.PaypalWebhook, '/webhook/paypal');
    api.addResource(resources.CoinSubWebhook, '/webhook/coinsub');
}

export function configureCreditor(app: Application): void {
    const api = new Api(app);
    api.addResource(resources.PaymentFulfillment, '/fulfillment/payment');
} 