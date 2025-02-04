import { AbstractWebhook } from './abstract/AbstractWebhook';
import { PaymentProvider } from '../../services/PaymentProvider';
import { GoogleVerifier } from '../../verifiers/GoogleVerifier';
import { Forwarder } from '../../services/forwarder/abstract/Forwarder';
import { OneTimePaymentData } from '../../services/store/payment/one_time/OneTimePaymentData';
import { SubscriptionPaymentData } from '../../services/store/payment/subscription/SubscriptionPaymentData';
import { ItemType } from '../../services/ItemType';
import { Logger } from '../../utils/Logger';
import { WebhookError } from '../../errors/WebhookError';

export class GoogleWebhookError extends WebhookError {}

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
    productId?: string;
    purchaseToken?: string;
    packageName?: string;
    isSubscription?: boolean;
    metadata?: Record<string, any>;
    voided?: boolean;
    acknowledgementState?: number;
}

export class GoogleWebhook extends AbstractWebhook<GoogleWebhookData, GoogleItemCategory> {
    private readonly verifier: GoogleVerifier;

    constructor(forwarder: Forwarder | null = null) {
        const verifier = new GoogleVerifier();
        super(
            PaymentProvider.GOOGLE,
            verifier,
            forwarder
        );
        this.verifier = verifier;
    }

    private mapStatus(notificationType: string): string {
        switch (notificationType) {
            case 'SUBSCRIPTION_PURCHASED':
            case 'SUBSCRIPTION_RENEWED':
            case 'SUBSCRIPTION_RESTARTED':
            case 'ONE_TIME_PRODUCT_PURCHASED':
                return 'paid';
            case 'SUBSCRIPTION_CANCELED':
            case 'SUBSCRIPTION_ON_HOLD':
            case 'SUBSCRIPTION_IN_GRACE_PERIOD':
            case 'SUBSCRIPTION_PRICE_CHANGE_CONFIRMED':
            case 'SUBSCRIPTION_DEFERRED':
            case 'SUBSCRIPTION_PAUSED':
            case 'SUBSCRIPTION_PAUSE_SCHEDULE_CHANGED':
            case 'SUBSCRIPTION_EXPIRED':
            case 'ONE_TIME_PRODUCT_CANCELED':
                return 'sent_to_processor';
            case 'SUBSCRIPTION_REVOKED':
            default:
                return 'webhook_received';
        }
    }

    protected async parseEventData(eventData: string): Promise<GoogleWebhookData> {
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
            const isSubscription = !!notification.subscriptionNotification;

            const webhookData: GoogleWebhookData = {
                transactionId: purchase.orderId,
                amount: parseFloat(purchase.priceAmountMicros || '0') / 1_000_000,
                currency: purchase.priceCurrencyCode || 'USD',
                status: status as GoogleWebhookData['status'],
                userId: notification.userId,
                subscriptionId: purchase.subscriptionId,
                productId: purchase.productId,
                purchaseToken: purchase.purchaseToken,
                packageName: notification.packageName,
                isSubscription,
                metadata: notification.developerPayload || {},
                voided: false,
                acknowledgementState: purchase.acknowledgementState || 0
            };

            // Verify purchase if we have the necessary data
            if (webhookData.purchaseToken && webhookData.productId) {
                try {
                    // Verify the purchase based on type
                    const verifyResult = isSubscription
                        ? await this.verifier.verifySubscription(webhookData.purchaseToken, webhookData.subscriptionId!)
                        : await this.verifier.verifyPurchase(webhookData.purchaseToken, webhookData.productId);

                    // Update webhook data with verification results
                    if (verifyResult.status === 'success') {
                        webhookData.metadata = {
                            ...webhookData.metadata,
                            verification: verifyResult,
                            productDetails: await this.verifier.getProductDetails(webhookData.productId)
                        };

                        // Check if purchase is in voided purchases list
                        const voidedPurchases = await this.verifier.getVoidedPurchases();
                        webhookData.voided = voidedPurchases.some(
                            vp => vp.purchaseToken === webhookData.purchaseToken
                        );
                    }

                    // Acknowledge the purchase if not already acknowledged
                    if (!webhookData.acknowledgementState) {
                        await this.verifier.acknowledgePurchase(
                            webhookData.purchaseToken,
                            webhookData.productId,
                            webhookData.isSubscription
                        );
                    }
                } catch (error) {
                    Logger.error('Purchase verification error:', error);
                    webhookData.metadata.verificationError = error.message;
                }
            }

            return webhookData;
        } catch (error) {
            throw new GoogleWebhookError(`Error parsing event data: ${error.message}`);
        }
    }

    protected itemNameProvider(eventData: GoogleWebhookData): string {
        try {
            if (eventData.metadata?.productDetails) {
                const productDetails = eventData.metadata.productDetails;
                return productDetails.listing?.title || this.fallbackItemName(eventData);
            }
            return this.fallbackItemName(eventData);
        } catch (error) {
            return this.fallbackItemName(eventData);
        }
    }

    private fallbackItemName(eventData: GoogleWebhookData): string {
        if (eventData.isSubscription) {
            return `Subscription: ${eventData.subscriptionId || ''}`;
        }
        return `Product: ${eventData.productId || ''}`;
    }

    protected getOneTimePaymentData(eventData: GoogleWebhookData): OneTimePaymentData<GoogleItemCategory> {
        return {
            userId: eventData.userId || '',
            itemCategory: GoogleItemCategory.ONE_TIME,
            purchaseId: eventData.transactionId,
            itemName: this.itemNameProvider(eventData),
            timeBought: new Date().toISOString(),
            status: eventData.status,
            quantity: 1,
            metadata: {
                ...eventData.metadata,
                productId: eventData.productId,
                purchaseToken: eventData.purchaseToken,
                packageName: eventData.packageName,
                voided: eventData.voided,
                acknowledgementState: eventData.acknowledgementState
            }
        };
    }

    protected getSubscriptionPaymentData(eventData: GoogleWebhookData): SubscriptionPaymentData<GoogleItemCategory> {
        const verificationData = eventData.metadata?.verification || {};
        const subscriptionData = verificationData.subscription || {};

        return {
            userId: eventData.userId || '',
            itemCategory: GoogleItemCategory.SUBSCRIPTION,
            purchaseId: eventData.transactionId,
            itemName: this.itemNameProvider(eventData),
            timeBought: new Date().toISOString(),
            status: eventData.status,
            metadata: {
                ...eventData.metadata,
                subscriptionId: eventData.subscriptionId,
                productId: eventData.productId,
                purchaseToken: eventData.purchaseToken,
                packageName: eventData.packageName,
                voided: eventData.voided,
                acknowledgementState: eventData.acknowledgementState,
                subscriptionData
            }
        };
    }
} 