import { PaymentProvider } from '../../PaymentProvider';
import { OneTimePaymentData } from './one_time/OneTimePaymentData';
import { SubscriptionPaymentData } from './subscription/SubscriptionPaymentData';
import { OneTimePaymentHandler, SubscriptionPaymentHandler } from './abstract/PaymentHandler';

export class PaymentService<ONE_TIME_ITEM_CATEGORY extends string, SUBSCRIPTION_ITEM_CATEGORY extends string> {
    private readonly enabledProviders: PaymentProvider[];
    private readonly oneTimeHandlers: Map<ONE_TIME_ITEM_CATEGORY, OneTimePaymentHandler<ONE_TIME_ITEM_CATEGORY>>;
    private readonly subscriptionHandlers: Map<SUBSCRIPTION_ITEM_CATEGORY, SubscriptionPaymentHandler<SUBSCRIPTION_ITEM_CATEGORY>>;

    constructor(enabledProviders: PaymentProvider[]) {
        this.enabledProviders = enabledProviders;
        this.oneTimeHandlers = new Map();
        this.subscriptionHandlers = new Map();
    }

    public registerOneTimeHandler(category: ONE_TIME_ITEM_CATEGORY, handler: OneTimePaymentHandler<ONE_TIME_ITEM_CATEGORY>): void {
        this.oneTimeHandlers.set(category, handler);
    }

    public registerSubscriptionHandler(category: SUBSCRIPTION_ITEM_CATEGORY, handler: SubscriptionPaymentHandler<SUBSCRIPTION_ITEM_CATEGORY>): void {
        this.subscriptionHandlers.set(category, handler);
    }

    public async handleOneTimePayment(
        provider: PaymentProvider,
        category: ONE_TIME_ITEM_CATEGORY,
        paymentData: OneTimePaymentData<ONE_TIME_ITEM_CATEGORY>
    ): Promise<void> {
        const handler = this.oneTimeHandlers.get(category);
        if (!handler) {
            throw new Error(`No handler registered for one-time payment category: ${category}`);
        }
        await handler.handlePayment(paymentData);
    }

    public async handleSubscriptionPayment(
        provider: PaymentProvider,
        category: SUBSCRIPTION_ITEM_CATEGORY,
        paymentData: SubscriptionPaymentData<SUBSCRIPTION_ITEM_CATEGORY>
    ): Promise<void> {
        const handler = this.subscriptionHandlers.get(category);
        if (!handler) {
            throw new Error(`No handler registered for subscription category: ${category}`);
        }
        await handler.handlePayment(paymentData);
    }
} 