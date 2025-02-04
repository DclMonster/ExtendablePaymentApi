import { AbstractWebhook } from './abstract/AbstractWebhook';
import { PaymentProvider } from '../../services/PaymentProvider';
import { PayPalVerifier } from '../../verifiers/PayPalVerifier';
import { Forwarder } from '../../services/forwarder/abstract/Forwarder';
import { OneTimePaymentData } from '../../services/store/payment/one_time/OneTimePaymentData';
import { SubscriptionPaymentData } from '../../services/store/payment/subscription/SubscriptionPaymentData';
import { Logger } from '../../utils/Logger';
import { WebhookError } from '../../errors/WebhookError';

export class PayPalWebhookError extends WebhookError {}

export enum PayPalItemCategory {
    ONE_TIME = 'ONE_TIME',
    SUBSCRIPTION = 'SUBSCRIPTION'
}

interface PayPalWebhookData {
    transactionId: string;
    amount: number;
    currency: string;
    status: 'webhook_received' | 'sent_to_websocket' | 'sent_to_processor' | 'paid';
    userId?: string;
    orderId?: string;
    subscriptionId?: string;
    metadata?: Record<string, any>;
    paymentInfo?: {
        intent: string;
        paymentMethod: string;
        payerId?: string;
        payerEmail?: string;
        createTime?: string;
        updateTime?: string;
    };
    billingInfo?: {
        cycleExecutions?: Array<{
            tenureType: string;
            sequence: number;
            cyclesCompleted: number;
            cyclesRemaining: number;
            currentPricingSchemeVersion: number;
        }>;
        lastPayment?: {
            amount: {
                currencyCode: string;
                value: string;
            };
            time: string;
        };
        nextBillingTime?: string;
        failedPaymentsCount?: number;
    };
}

export class PayPalWebhook extends AbstractWebhook<PayPalWebhookData, PayPalItemCategory> {
    private readonly verifier: PayPalVerifier;

    constructor(forwarder: Forwarder | null = null) {
        const verifier = new PayPalVerifier();
        super(
            PaymentProvider.PAYPAL,
            verifier,
            forwarder
        );
        this.verifier = verifier;
    }

    private mapStatus(eventType: string): string {
        switch (eventType) {
            case 'PAYMENT.CAPTURE.COMPLETED':
            case 'PAYMENT.SALE.COMPLETED':
            case 'BILLING.SUBSCRIPTION.ACTIVATED':
            case 'BILLING.SUBSCRIPTION.RENEWED':
                return 'paid';
            case 'PAYMENT.CAPTURE.PENDING':
            case 'PAYMENT.SALE.PENDING':
            case 'PAYMENT.CAPTURE.DENIED':
            case 'PAYMENT.SALE.DENIED':
            case 'BILLING.SUBSCRIPTION.SUSPENDED':
            case 'BILLING.SUBSCRIPTION.CANCELLED':
            case 'BILLING.SUBSCRIPTION.EXPIRED':
                return 'sent_to_processor';
            case 'CHECKOUT.ORDER.APPROVED':
            case 'BILLING.SUBSCRIPTION.CREATED':
                return 'sent_to_websocket';
            default:
                return 'webhook_received';
        }
    }

    protected async parseEventData(eventData: string): Promise<PayPalWebhookData> {
        try {
            const data = JSON.parse(eventData);
            if (!data || !data.event_type || !data.resource) {
                throw new PayPalWebhookError('No JSON data, event type, or resource in request');
            }

            const resource = data.resource;
            const isSubscription = data.event_type.startsWith('BILLING.SUBSCRIPTION');

            const status = this.mapStatus(data.event_type);
            const amount = resource.amount || resource.billing_info?.last_payment?.amount || { value: '0' };

            const webhookData: PayPalWebhookData = {
                transactionId: resource.id,
                amount: parseFloat(amount.value),
                currency: amount.currency_code || 'USD',
                status: status as PayPalWebhookData['status'],
                userId: resource.custom_id,
                orderId: resource.order_id || resource.id,
                subscriptionId: isSubscription ? resource.id : undefined,
                metadata: {
                    eventType: data.event_type,
                    summary: data.summary,
                    resource_type: data.resource_type,
                    resource_version: data.resource_version,
                    status: resource.status,
                    links: resource.links
                }
            };

            // Add payment info for orders
            if (!isSubscription) {
                webhookData.paymentInfo = {
                    intent: resource.intent,
                    paymentMethod: resource.payment_source?.paypal ? 'paypal' : 'card',
                    payerId: resource.payer?.payer_id,
                    payerEmail: resource.payer?.email_address,
                    createTime: resource.create_time,
                    updateTime: resource.update_time
                };

                // Verify the order
                try {
                    const verifiedOrder = await this.verifier.verifyOrder(webhookData.orderId!);
                    webhookData.metadata = {
                        ...webhookData.metadata,
                        verification: verifiedOrder
                    };
                } catch (error) {
                    Logger.error('Order verification error:', error);
                    webhookData.metadata.verificationError = error.message;
                }
            } else {
                // Add billing info for subscriptions
                webhookData.billingInfo = {
                    cycleExecutions: resource.billing_info?.cycle_executions,
                    lastPayment: resource.billing_info?.last_payment,
                    nextBillingTime: resource.billing_info?.next_billing_time,
                    failedPaymentsCount: resource.billing_info?.failed_payments_count
                };

                // Verify the subscription
                try {
                    const verifiedSubscription = await this.verifier.verifySubscription(webhookData.subscriptionId!);
                    webhookData.metadata = {
                        ...webhookData.metadata,
                        verification: verifiedSubscription
                    };
                } catch (error) {
                    Logger.error('Subscription verification error:', error);
                    webhookData.metadata.verificationError = error.message;
                }
            }

            return webhookData;
        } catch (error) {
            throw new PayPalWebhookError(`Error parsing event data: ${error.message}`);
        }
    }

    protected itemNameProvider(eventData: PayPalWebhookData): string {
        try {
            const verificationData = eventData.metadata?.verification;
            if (verificationData) {
                if ('purchase_units' in verificationData) {
                    return verificationData.purchase_units[0]?.description || this.fallbackItemName(eventData);
                }
                if ('plan_id' in verificationData) {
                    return `Subscription: ${verificationData.plan_id}`;
                }
            }
            return this.fallbackItemName(eventData);
        } catch (error) {
            return this.fallbackItemName(eventData);
        }
    }

    private fallbackItemName(eventData: PayPalWebhookData): string {
        if (eventData.subscriptionId) {
            return `Subscription: ${eventData.subscriptionId}`;
        }
        return `Order: ${eventData.orderId || eventData.transactionId}`;
    }

    protected getOneTimePaymentData(eventData: PayPalWebhookData): OneTimePaymentData<PayPalItemCategory> {
        return {
            userId: eventData.userId || '',
            itemCategory: PayPalItemCategory.ONE_TIME,
            purchaseId: eventData.transactionId,
            itemName: this.itemNameProvider(eventData),
            timeBought: new Date().toISOString(),
            status: eventData.status,
            quantity: 1,
            metadata: {
                ...eventData.metadata,
                orderId: eventData.orderId,
                paymentInfo: eventData.paymentInfo
            }
        };
    }

    protected getSubscriptionPaymentData(eventData: PayPalWebhookData): SubscriptionPaymentData<PayPalItemCategory> {
        const verificationData = eventData.metadata?.verification || {};

        return {
            userId: eventData.userId || '',
            itemCategory: PayPalItemCategory.SUBSCRIPTION,
            purchaseId: eventData.transactionId,
            itemName: this.itemNameProvider(eventData),
            timeBought: new Date().toISOString(),
            status: eventData.status,
            metadata: {
                ...eventData.metadata,
                subscriptionId: eventData.subscriptionId,
                billingInfo: eventData.billingInfo,
                verificationData
            }
        };
    }
} 