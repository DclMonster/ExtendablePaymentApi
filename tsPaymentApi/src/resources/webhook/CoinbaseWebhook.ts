import { AbstractWebhook } from './abstract/AbstractWebhook';
import { PaymentProvider } from '../../services/PaymentProvider';
import { CoinbaseVerifier } from '../../verifiers/CoinbaseVerifier';
import { Forwarder } from '../../services/forwarder/abstract/Forwarder';
import { OneTimePaymentData } from '../../services/store/payment/one_time/OneTimePaymentData';
import { SubscriptionPaymentData } from '../../services/store/payment/subscription/SubscriptionPaymentData';
import { Logger } from '../../utils/Logger';
import { WebhookError } from '../../errors/WebhookError';

export class CoinbaseWebhookError extends WebhookError {}

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
    chargeId?: string;
    chargeCode?: string;
    metadata?: Record<string, any>;
    pricing?: {
        local: {
            amount: string;
            currency: string;
        };
        crypto?: {
            amount: string;
            currency: string;
        };
    };
    addresses?: Record<string, string>;
    hostedUrl?: string;
    expiresAt?: string;
}

export class CoinbaseWebhook extends AbstractWebhook<CoinbaseWebhookData, CoinbaseItemCategory> {
    private readonly verifier: CoinbaseVerifier;

    constructor(forwarder: Forwarder | null = null) {
        const verifier = new CoinbaseVerifier();
        super(
            PaymentProvider.COINBASE,
            verifier,
            forwarder
        );
        this.verifier = verifier;
    }

    private mapStatus(eventType: string): string {
        switch (eventType) {
            case 'charge:confirmed':
            case 'charge:resolved':
                return 'paid';
            case 'charge:failed':
            case 'charge:delayed':
            case 'charge:pending':
                return 'sent_to_processor';
            case 'charge:created':
                return 'sent_to_websocket';
            default:
                return 'webhook_received';
        }
    }

    protected async parseEventData(eventData: string): Promise<CoinbaseWebhookData> {
        try {
            const data = JSON.parse(eventData);
            if (!data || !data.event) {
                throw new CoinbaseWebhookError('No JSON data or event in request');
            }

            const event = data.event;
            const charge = event.data;

            if (!charge) {
                throw new CoinbaseWebhookError('No charge data in event');
            }

            const status = this.mapStatus(event.type);

            const webhookData: CoinbaseWebhookData = {
                transactionId: charge.id,
                amount: parseFloat(charge.pricing?.local?.amount || '0'),
                currency: charge.pricing?.local?.currency || 'USD',
                status: status as CoinbaseWebhookData['status'],
                userId: charge.metadata?.userId,
                chargeId: charge.id,
                chargeCode: charge.code,
                metadata: {
                    ...charge.metadata,
                    eventType: event.type,
                    timeline: charge.timeline,
                    payments: charge.payments
                },
                pricing: charge.pricing,
                addresses: charge.addresses,
                hostedUrl: charge.hosted_url,
                expiresAt: charge.expires_at
            };

            // Verify the charge
            try {
                const verifiedCharge = await this.verifier.verifyCharge(webhookData.chargeId);
                webhookData.metadata = {
                    ...webhookData.metadata,
                    verification: verifiedCharge
                };
            } catch (error) {
                Logger.error('Charge verification error:', error);
                webhookData.metadata.verificationError = error.message;
            }

            return webhookData;
        } catch (error) {
            throw new CoinbaseWebhookError(`Error parsing event data: ${error.message}`);
        }
    }

    protected itemNameProvider(eventData: CoinbaseWebhookData): string {
        try {
            const verificationData = eventData.metadata?.verification;
            if (verificationData) {
                return verificationData.name || this.fallbackItemName(eventData);
            }
            return this.fallbackItemName(eventData);
        } catch (error) {
            return this.fallbackItemName(eventData);
        }
    }

    private fallbackItemName(eventData: CoinbaseWebhookData): string {
        return `Charge: ${eventData.chargeCode || eventData.chargeId || ''}`;
    }

    protected getOneTimePaymentData(eventData: CoinbaseWebhookData): OneTimePaymentData<CoinbaseItemCategory> {
        return {
            userId: eventData.userId || '',
            itemCategory: CoinbaseItemCategory.ONE_TIME,
            purchaseId: eventData.transactionId,
            itemName: this.itemNameProvider(eventData),
            timeBought: new Date().toISOString(),
            status: eventData.status,
            quantity: 1,
            metadata: {
                ...eventData.metadata,
                chargeId: eventData.chargeId,
                chargeCode: eventData.chargeCode,
                pricing: eventData.pricing,
                addresses: eventData.addresses,
                hostedUrl: eventData.hostedUrl,
                expiresAt: eventData.expiresAt
            }
        };
    }

    protected getSubscriptionPaymentData(eventData: CoinbaseWebhookData): SubscriptionPaymentData<CoinbaseItemCategory> {
        const verificationData = eventData.metadata?.verification || {};

        return {
            userId: eventData.userId || '',
            itemCategory: CoinbaseItemCategory.SUBSCRIPTION,
            purchaseId: eventData.transactionId,
            itemName: this.itemNameProvider(eventData),
            timeBought: new Date().toISOString(),
            status: eventData.status,
            metadata: {
                ...eventData.metadata,
                chargeId: eventData.chargeId,
                chargeCode: eventData.chargeCode,
                pricing: eventData.pricing,
                addresses: eventData.addresses,
                hostedUrl: eventData.hostedUrl,
                expiresAt: eventData.expiresAt,
                verificationData
            }
        };
    }
} 