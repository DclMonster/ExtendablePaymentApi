import { AbstractWebhook } from './abstract/AbstractWebhook';
import { PaymentProvider } from '../../services/PaymentProvider';
import { SignatureVerifier } from '../../verifiers/SignatureVerifier';
import { Forwarder } from '../../services/forwarder/abstract/Forwarder';
import { OneTimePaymentData } from '../../services/store/payment/one_time/OneTimePaymentData';
import { SubscriptionPaymentData } from '../../services/store/payment/subscription/SubscriptionPaymentData';
import { ItemType } from '../../services/ItemType';

export class GoogleWebhookError extends Error {
    constructor(message: string) {
        super(message);
        this.name = 'GoogleWebhookError';
    }
}

export enum GoogleItemCategory {
    ONE_TIME = 'ONE_TIME',
    SUBSCRIPTION = 'SUBSCRIPTION'
}

interface GoogleWebhookData {
    transactionId: string;
    amount: number;
    currency: string;
    status: 'webhook_received' | 'sent_to_websocket' | 'sent_to_processor' | 'paid';
    userId?: string;
    subscriptionId?: string;
}

export class GoogleWebhook extends AbstractWebhook<GoogleWebhookData, GoogleItemCategory> {
    constructor(forwarder: Forwarder | null = null) {
        super(
            PaymentProvider.GOOGLE,
            // This should be replaced with actual Google signature verification
            {
                verifyHeaderSignature: () => {}
            },
            forwarder
        );
    }

    private mapStatus(notificationType: string): string {
        switch (notificationType) {
            case 'SUBSCRIPTION_PURCHASED':
            case 'SUBSCRIPTION_RENEWED':
            case 'SUBSCRIPTION_RESTARTED':
                return 'paid';
            case 'SUBSCRIPTION_CANCELED':
            case 'SUBSCRIPTION_ON_HOLD':
            case 'SUBSCRIPTION_IN_GRACE_PERIOD':
            case 'SUBSCRIPTION_PRICE_CHANGE_CONFIRMED':
            case 'SUBSCRIPTION_DEFERRED':
            case 'SUBSCRIPTION_PAUSED':
            case 'SUBSCRIPTION_PAUSE_SCHEDULE_CHANGED':
            case 'SUBSCRIPTION_EXPIRED':
                return 'sent_to_processor';
            case 'SUBSCRIPTION_REVOKED':
            default:
                return 'webhook_received';
        }
    }

    protected parseEventData(eventData: string): GoogleWebhookData {
        try {
            const data = JSON.parse(eventData);
            if (!data) {
                throw new GoogleWebhookError('No JSON data in request');
            }

            const notification = data.message?.data ?? {};
            const purchase = notification.subscriptionNotification || notification.oneTimeProductNotification || {};

            const requiredFields = ['orderId', 'priceAmountMicros', 'priceCurrencyCode', 'notificationType'];
            const missingFields = requiredFields.filter(field => !(field in purchase));
            if (missingFields.length > 0) {
                throw new GoogleWebhookError(`Missing required fields: ${missingFields.join(', ')}`);
            }

            const status = this.mapStatus(purchase.notificationType);

            return {
                transactionId: purchase.orderId,
                amount: parseFloat(purchase.priceAmountMicros || '0') / 1_000_000, // Convert micros to standard currency
                currency: purchase.priceCurrencyCode || 'USD',
                status: status as GoogleWebhookData['status'],
                userId: notification.userId,
                subscriptionId: purchase.subscriptionId
            };
        } catch (error) {
            throw new GoogleWebhookError(`Error parsing event data: ${error}`);
        }
    }

    protected itemNameProvider(eventData: GoogleWebhookData): string {
        return eventData.subscriptionId || '';
    }

    protected getOneTimePaymentData(eventData: GoogleWebhookData): OneTimePaymentData<GoogleItemCategory> {
        return {
            userId: eventData.userId || '',
            itemCategory: GoogleItemCategory.ONE_TIME,
            purchaseId: eventData.transactionId,
            itemName: this.itemNameProvider(eventData),
            timeBought: new Date().toISOString(),
            status: eventData.status,
            quantity: 1
        };
    }

    protected getSubscriptionPaymentData(eventData: GoogleWebhookData): SubscriptionPaymentData<GoogleItemCategory> {
        return {
            userId: eventData.userId || '',
            itemCategory: GoogleItemCategory.SUBSCRIPTION,
            purchaseId: eventData.transactionId,
            itemName: this.itemNameProvider(eventData),
            timeBought: new Date().toISOString(),
            status: eventData.status
        };
    }
} 