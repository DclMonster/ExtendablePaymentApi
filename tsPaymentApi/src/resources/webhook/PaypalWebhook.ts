import { AbstractWebhook } from './abstract/AbstractWebhook';
import { PaymentProvider } from '../../services/PaymentProvider';
import { SignatureVerifier } from '../../verifiers/SignatureVerifier';
import { Forwarder } from '../../services/forwarder/abstract/Forwarder';
import { OneTimePaymentData } from '../../services/store/payment/one_time/OneTimePaymentData';
import { SubscriptionPaymentData } from '../../services/store/payment/subscription/SubscriptionPaymentData';

enum PaypalItemCategory {
    STANDARD = 'STANDARD'
}

interface PaypalEventData {
    itemName: string;
    amount: number;
    purchaseId: string;
    userId: string;
}

export class PaypalWebhook extends AbstractWebhook<PaypalEventData, PaypalItemCategory> {
    constructor(forwarder: Forwarder | null = null) {
        super(
            PaymentProvider.PAYPAL,
            // This should be replaced with actual PayPal signature verification
            {
                verifyHeaderSignature: () => {}
            },
            forwarder
        );
    }

    protected getOneTimePaymentData(eventData: PaypalEventData): OneTimePaymentData<PaypalItemCategory> {
        return new OneTimePaymentData(
            eventData.itemName,
            eventData.amount,
            eventData.purchaseId,
            eventData.userId,
            new Date().toISOString(),
            'SENT_TO_WEBSOCKET',
            PaypalItemCategory.STANDARD
        );
    }

    protected getSubscriptionPaymentData(eventData: PaypalEventData): SubscriptionPaymentData<PaypalItemCategory> {
        return new SubscriptionPaymentData(
            eventData.itemName,
            PaypalItemCategory.STANDARD,
            eventData.purchaseId,
            eventData.userId,
            new Date().toISOString(),
            'SENT_TO_WEBSOCKET'
        );
    }

    protected itemNameProvider(eventData: PaypalEventData): string {
        return eventData.itemName;
    }

    protected parseEventData(eventData: string): PaypalEventData {
        // This should be replaced with actual PayPal event data parsing
        const data = JSON.parse(eventData);
        return {
            itemName: data.itemName || 'default_item',
            amount: data.amount || 0,
            purchaseId: data.purchaseId || 'default_purchase_id',
            userId: data.userId || 'default_user_id'
        };
    }
} 