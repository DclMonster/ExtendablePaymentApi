import { AbstractWebhook } from './abstract/AbstractWebhook';
import { PaymentProvider } from '../../services/PaymentProvider';
import { AppleVerifier } from '../../verifiers/AppleVerifier';
import { Forwarder } from '../../services/forwarder/abstract/Forwarder';
import { OneTimePaymentData } from '../../services/store/payment/one_time/OneTimePaymentData';
import { SubscriptionPaymentData } from '../../services/store/payment/subscription/SubscriptionPaymentData';
import { ItemType } from '../../services/ItemType';
import { Logger } from '../../utils/Logger';
import { WebhookError } from '../../errors/WebhookError';

export class AppleWebhookError extends WebhookError {}

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
    productId?: string;
    receiptData?: string;
    bundleId?: string;
    isSubscription?: boolean;
    metadata?: Record<string, any>;
    environment?: 'Production' | 'Sandbox';
    isRetryable?: boolean;
}

export class AppleWebhook extends AbstractWebhook<AppleWebhookData, AppleItemCategory> {
    private readonly verifier: AppleVerifier;

    constructor(forwarder: Forwarder | null = null) {
        const verifier = new AppleVerifier();
        super(
            PaymentProvider.APPLE,
            verifier,
            forwarder
        );
        this.verifier = verifier;
    }

    private mapStatus(notificationType: string, status: string = ''): string {
        switch (notificationType) {
            case 'INITIAL_BUY':
            case 'DID_RENEW':
            case 'INTERACTIVE_RENEWAL':
                return 'paid';
            case 'DID_CHANGE_RENEWAL_PREF':
            case 'CANCEL':
            case 'DID_CHANGE_RENEWAL_STATUS':
            case 'PRICE_INCREASE_CONSENT':
            case 'REFUND':
            case 'REVOKE':
            case 'CONSUMPTION_REQUEST':
                return 'sent_to_processor';
            case 'DID_FAIL_TO_RENEW':
            default:
                return 'webhook_received';
        }
    }

    protected async parseEventData(eventData: string): Promise<AppleWebhookData> {
        try {
            const data = JSON.parse(eventData);
            if (!data) {
                throw new AppleWebhookError('No JSON data in request');
            }

            const notificationType = data.notification_type;
            const receiptInfo = data.unified_receipt?.latest_receipt_info?.[0] ?? {};
            const environment = data.environment || 'Production';

            const requiredFields = ['transaction_id', 'price', 'currency'];
            const missingFields = requiredFields.filter(field => !(field in receiptInfo));
            if (missingFields.length > 0) {
                throw new AppleWebhookError(`Missing required fields: ${missingFields.join(', ')}`);
            }

            const status = this.mapStatus(notificationType, receiptInfo.status);
            const isSubscription = !!receiptInfo.expires_date;

            const webhookData: AppleWebhookData = {
                transactionId: receiptInfo.transaction_id,
                amount: parseFloat(receiptInfo.price || '0'),
                currency: receiptInfo.currency || 'USD',
                status: status as AppleWebhookData['status'],
                userId: data.user_id,
                subscriptionId: receiptInfo.product_id,
                productId: receiptInfo.product_id,
                receiptData: data.latest_receipt,
                bundleId: receiptInfo.bid,
                isSubscription,
                metadata: {
                    notificationType,
                    webOrderLineItemId: receiptInfo.web_order_line_item_id,
                    isTrialPeriod: receiptInfo.is_trial_period === 'true',
                    isInIntroOfferPeriod: receiptInfo.is_in_intro_offer_period === 'true',
                    originalTransactionId: receiptInfo.original_transaction_id,
                    promotionalOfferId: receiptInfo.promotional_offer_id,
                    offerCodeRefName: receiptInfo.offer_code_ref_name
                },
                environment,
                isRetryable: data['is-retryable'] ?? true
            };

            // Verify receipt if we have the necessary data
            if (webhookData.receiptData) {
                try {
                    const verifyResult = await this.verifier.verifyReceipt(
                        webhookData.receiptData,
                        webhookData.environment?.toLowerCase() === 'sandbox'
                    );

                    // Update webhook data with verification results
                    if (verifyResult.status === 'success') {
                        webhookData.metadata = {
                            ...webhookData.metadata,
                            verification: verifyResult,
                            receiptVerification: verifyResult.subscription || verifyResult.item
                        };
                    }
                } catch (error) {
                    Logger.error('Receipt verification error:', error);
                    webhookData.metadata.verificationError = error.message;
                }
            }

            return webhookData;
        } catch (error) {
            throw new AppleWebhookError(`Error parsing event data: ${error.message}`);
        }
    }

    protected itemNameProvider(eventData: AppleWebhookData): string {
        try {
            const receiptData = eventData.metadata?.receiptVerification;
            if (receiptData) {
                const productId = receiptData.productId;
                if (productId) {
                    return `Product: ${productId}`;
                }
            }
            return this.fallbackItemName(eventData);
        } catch (error) {
            return this.fallbackItemName(eventData);
        }
    }

    private fallbackItemName(eventData: AppleWebhookData): string {
        if (eventData.isSubscription) {
            return `Subscription: ${eventData.subscriptionId || ''}`;
        }
        return `Product: ${eventData.productId || ''}`;
    }

    protected getOneTimePaymentData(eventData: AppleWebhookData): OneTimePaymentData<AppleItemCategory> {
        return {
            userId: eventData.userId || '',
            itemCategory: AppleItemCategory.ONE_TIME,
            purchaseId: eventData.transactionId,
            itemName: this.itemNameProvider(eventData),
            timeBought: new Date().toISOString(),
            status: eventData.status,
            quantity: 1,
            metadata: {
                ...eventData.metadata,
                productId: eventData.productId,
                bundleId: eventData.bundleId,
                environment: eventData.environment,
                isRetryable: eventData.isRetryable
            }
        };
    }

    protected getSubscriptionPaymentData(eventData: AppleWebhookData): SubscriptionPaymentData<AppleItemCategory> {
        const verificationData = eventData.metadata?.verification || {};
        const receiptData = verificationData.subscription || {};

        return {
            userId: eventData.userId || '',
            itemCategory: AppleItemCategory.SUBSCRIPTION,
            purchaseId: eventData.transactionId,
            itemName: this.itemNameProvider(eventData),
            timeBought: new Date().toISOString(),
            status: eventData.status,
            metadata: {
                ...eventData.metadata,
                subscriptionId: eventData.subscriptionId,
                productId: eventData.productId,
                bundleId: eventData.bundleId,
                environment: eventData.environment,
                isRetryable: eventData.isRetryable,
                receiptData
            }
        };
    }
} 