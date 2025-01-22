import { AbstractWebhook } from './abstract/AbstractWebhook';
import { PaymentProvider } from '../../services/PaymentProvider';
import { SignatureVerifier } from '../../verifiers/SignatureVerifier';
import { Forwarder } from '../../services/forwarder/abstract/Forwarder';
import { OneTimePaymentData } from '../../services/store/payment/one_time/OneTimePaymentData';
import { SubscriptionPaymentData } from '../../services/store/payment/subscription/SubscriptionPaymentData';
import { ItemType } from '../../services/ItemType';

export class AppleWebhookError extends Error {
    constructor(message: string) {
        super(message);
        this.name = 'AppleWebhookError';
    }
}

export enum AppleItemCategory {
    ONE_TIME = 'ONE_TIME',
    SUBSCRIPTION = 'SUBSCRIPTION'
}

interface AppleWebhookData {
    transactionId: string;
    amount: number;
    currency: string;
    status: 'webhook_received' | 'sent_to_websocket' | 'sent_to_processor' | 'paid';
    userId?: string;
    subscriptionId?: string;
}

export class AppleWebhook extends AbstractWebhook<AppleWebhookData, AppleItemCategory> {
    constructor(forwarder: Forwarder | null = null) {
        super(
            PaymentProvider.APPLE,
            // This should be replaced with actual Apple signature verification
            {
                verifyHeaderSignature: () => {}
            },
            forwarder
        );
    }

    private mapStatus(notificationType: string): string {
        switch (notificationType) {
            case 'INITIAL_BUY':
            case 'DID_RENEW':
                return 'paid';
            case 'CANCEL':
                return 'sent_to_processor';
            case 'DID_FAIL_TO_RENEW':
            default:
                return 'webhook_received';
        }
    }

    protected parseEventData(eventData: string): AppleWebhookData {
        try {
            const data = JSON.parse(eventData);
            if (!data) {
                throw new AppleWebhookError('No JSON data in request');
            }

            const notificationType = data.notificationType;
            const receiptInfo = data.unifiedReceipt?.latestReceiptInfo?.[0] ?? {};

            const requiredFields = ['transactionId', 'price', 'currency'];
            const missingFields = requiredFields.filter(field => !(field in receiptInfo));
            if (missingFields.length > 0) {
                throw new AppleWebhookError(`Missing required fields: ${missingFields.join(', ')}`);
            }

            const status = this.mapStatus(notificationType);

            return {
                transactionId: receiptInfo.transactionId,
                amount: parseFloat(receiptInfo.price || '0'),
                currency: receiptInfo.currency || 'USD',
                status: status as AppleWebhookData['status'],
                userId: data.userId,
                subscriptionId: receiptInfo.productId
            };
        } catch (error) {
            throw new AppleWebhookError(`Error parsing event data: ${error}`);
        }
    }

    protected itemNameProvider(eventData: AppleWebhookData): string {
        return 'Apple Payment';
    }

    protected getOneTimePaymentData(eventData: AppleWebhookData): OneTimePaymentData<AppleItemCategory> {
        return {
            userId: eventData.userId || '',
            itemCategory: AppleItemCategory.ONE_TIME,
            purchaseId: eventData.transactionId,
            itemName: this.itemNameProvider(eventData),
            timeBought: new Date().toISOString(),
            status: eventData.status,
            quantity: 1
        };
    }

    protected getSubscriptionPaymentData(eventData: AppleWebhookData): SubscriptionPaymentData<AppleItemCategory> {
        return {
            userId: eventData.userId || '',
            itemCategory: AppleItemCategory.SUBSCRIPTION,
            purchaseId: eventData.transactionId,
            itemName: this.itemNameProvider(eventData),
            timeBought: new Date().toISOString(),
            status: eventData.status
        };
    }
} 