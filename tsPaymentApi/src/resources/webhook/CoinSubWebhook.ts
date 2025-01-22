import { AbstractWebhook } from './abstract/AbstractWebhook';
import { PaymentProvider } from '../../services/PaymentProvider';
import { SignatureVerifier } from '../../verifiers/SignatureVerifier';
import { Forwarder } from '../../services/forwarder/abstract/Forwarder';
import { OneTimePaymentData } from '../../services/store/payment/one_time/OneTimePaymentData';
import { SubscriptionPaymentData } from '../../services/store/payment/subscription/SubscriptionPaymentData';
import { ItemType } from '../../services/ItemType';

export class CoinSubWebhookError extends Error {
    constructor(message: string) {
        super(message);
        this.name = 'CoinSubWebhookError';
    }
}

export enum CoinSubItemCategory {
    ONE_TIME = 'ONE_TIME',
    SUBSCRIPTION = 'SUBSCRIPTION'
}

interface CoinSubWebhookData {
    transactionId: string;
    amount: number;
    currency: string;
    status: 'webhook_received' | 'sent_to_websocket' | 'sent_to_processor' | 'paid';
    userId?: string;
    subscriptionId?: string;
}

export class CoinSubWebhook extends AbstractWebhook<CoinSubWebhookData, CoinSubItemCategory> {
    constructor(forwarder: Forwarder | null = null) {
        super(
            PaymentProvider.COINSUB,
            // This should be replaced with actual CoinSub signature verification
            {
                verifyHeaderSignature: () => {}
            },
            forwarder
        );
    }

    private mapStatus(eventType: string, status: string): string {
        switch (eventType) {
            case 'subscription_activated':
            case 'subscription_renewed':
                return 'paid';
            case 'subscription_canceled':
            case 'subscription_expired':
                return 'sent_to_processor';
            case 'subscription_created':
            case 'subscription_failed':
            default:
                return 'webhook_received';
        }
    }

    protected parseEventData(eventData: string): CoinSubWebhookData {
        try {
            const data = JSON.parse(eventData);
            if (!data) {
                throw new CoinSubWebhookError('No JSON data in request');
            }

            const eventType = data.event_type;
            const subscription = data.subscription || {};

            const requiredFields = ['transaction_id', 'amount', 'currency', 'status'];
            const missingFields = requiredFields.filter(field => !(field in subscription));
            if (missingFields.length > 0) {
                throw new CoinSubWebhookError(`Missing required fields: ${missingFields.join(', ')}`);
            }

            const status = this.mapStatus(eventType, subscription.status);

            return {
                transactionId: subscription.transaction_id,
                amount: parseFloat(subscription.amount || '0'),
                currency: subscription.currency || 'USD',
                status: status as CoinSubWebhookData['status'],
                userId: subscription.user_id,
                subscriptionId: subscription.subscription_id
            };
        } catch (error) {
            throw new CoinSubWebhookError(`Error parsing event data: ${error}`);
        }
    }

    protected itemNameProvider(eventData: CoinSubWebhookData): string {
        return eventData.subscriptionId || '';
    }

    protected getOneTimePaymentData(eventData: CoinSubWebhookData): OneTimePaymentData<CoinSubItemCategory> {
        return {
            userId: eventData.userId || '',
            itemCategory: CoinSubItemCategory.ONE_TIME,
            purchaseId: eventData.transactionId,
            itemName: this.itemNameProvider(eventData),
            timeBought: new Date().toISOString(),
            status: eventData.status,
            quantity: 1
        };
    }

    protected getSubscriptionPaymentData(eventData: CoinSubWebhookData): SubscriptionPaymentData<CoinSubItemCategory> {
        return {
            userId: eventData.userId || '',
            itemCategory: CoinSubItemCategory.SUBSCRIPTION,
            purchaseId: eventData.transactionId,
            itemName: this.itemNameProvider(eventData),
            timeBought: new Date().toISOString(),
            status: eventData.status
        };
    }
} 