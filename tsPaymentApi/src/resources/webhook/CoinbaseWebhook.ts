import { AbstractWebhook } from './abstract/AbstractWebhook';
import { PaymentProvider } from '../../services/PaymentProvider';
import { SignatureVerifier } from '../../verifiers/SignatureVerifier';
import { Forwarder } from '../../services/forwarder/abstract/Forwarder';
import { OneTimePaymentData } from '../../services/store/payment/one_time/OneTimePaymentData';
import { SubscriptionPaymentData } from '../../services/store/payment/subscription/SubscriptionPaymentData';
import { ItemType } from '../../services/ItemType';

export class CoinbaseWebhookError extends Error {
    constructor(message: string) {
        super(message);
        this.name = 'CoinbaseWebhookError';
    }
}

export enum CoinbaseItemCategory {
    ONE_TIME = 'ONE_TIME',
    SUBSCRIPTION = 'SUBSCRIPTION'
}

interface CoinbaseWebhookData {
    transactionId: string;
    amount: number;
    currency: string;
    status: 'webhook_received' | 'sent_to_websocket' | 'sent_to_processor' | 'paid';
    userId?: string;
    subscriptionId?: string;
}

export class CoinbaseWebhook extends AbstractWebhook<CoinbaseWebhookData, CoinbaseItemCategory> {
    constructor(forwarder: Forwarder | null = null) {
        super(
            PaymentProvider.COINBASE,
            // This should be replaced with actual Coinbase signature verification
            {
                verifyHeaderSignature: () => {}
            },
            forwarder
        );
    }

    private mapStatus(eventType: string, status: string): string {
        switch (eventType) {
            case 'charge:confirmed':
                return status === 'completed' ? 'paid' : 'webhook_received';
            case 'charge:resolved':
                return 'paid';
            case 'charge:pending':
                return 'sent_to_websocket';
            case 'charge:delayed':
                return 'sent_to_processor';
            case 'charge:created':
            case 'charge:failed':
            default:
                return 'webhook_received';
        }
    }

    protected parseEventData(eventData: string): CoinbaseWebhookData {
        try {
            const data = JSON.parse(eventData);
            if (!data) {
                throw new CoinbaseWebhookError('No JSON data in request');
            }

            const event = data.event || {};
            const eventType = event.type;
            const chargeData = event.data || {};

            const requiredFields = ['code'];
            const missingFields = requiredFields.filter(field => !(field in chargeData));
            if (missingFields.length > 0) {
                throw new CoinbaseWebhookError(`Missing required fields: ${missingFields.join(', ')}`);
            }

            const pricing = chargeData.pricing?.local || {};
            const status = this.mapStatus(eventType, chargeData.status || '');

            return {
                transactionId: chargeData.code,
                amount: parseFloat(pricing.amount || '0'),
                currency: pricing.currency || 'USD',
                status: status as CoinbaseWebhookData['status'],
                userId: chargeData.metadata?.user_id,
                subscriptionId: chargeData.metadata?.subscription_id
            };
        } catch (error) {
            throw new CoinbaseWebhookError(`Error parsing event data: ${error}`);
        }
    }

    protected itemNameProvider(eventData: CoinbaseWebhookData): string {
        return 'Coinbase Payment';
    }

    protected getOneTimePaymentData(eventData: CoinbaseWebhookData): OneTimePaymentData<CoinbaseItemCategory> {
        return {
            userId: eventData.userId || '',
            itemCategory: CoinbaseItemCategory.ONE_TIME,
            purchaseId: eventData.transactionId,
            itemName: this.itemNameProvider(eventData),
            timeBought: new Date().toISOString(),
            status: eventData.status,
            quantity: 1
        };
    }

    protected getSubscriptionPaymentData(eventData: CoinbaseWebhookData): SubscriptionPaymentData<CoinbaseItemCategory> {
        return {
            userId: eventData.userId || '',
            itemCategory: CoinbaseItemCategory.SUBSCRIPTION,
            purchaseId: eventData.transactionId,
            itemName: this.itemNameProvider(eventData),
            timeBought: new Date().toISOString(),
            status: eventData.status
        };
    }
} 