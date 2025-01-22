import { PaymentProvider } from './PaymentProvider';
import { ItemType } from './ItemType';
import { AvailableItem } from './store/AvailableItem';
import { PurchaseDetail } from './store/payment/PurchaseDetail';
import { PurchaseStatus } from './store/payment/PurchaseStatus';
import { OneTimePaymentData } from './store/payment/one_time/OneTimePaymentData';
import { SubscriptionPaymentData } from './store/payment/subscription/SubscriptionPaymentData';
import { ItemCollectionService } from './store/payment/abstract/ItemCollectionService';
import { OneTimePaymentHandler, SubscriptionPaymentHandler } from './store/payment/abstract/PaymentHandler';
import { StoreService } from './store/StoreService';
import { PaymentService } from './store/payment/PaymentService';

export class ServiceNotEnabledError extends Error {
    constructor(message: string) {
        super(message);
        this.name = 'ServiceNotEnabledError';
    }
}

export class Services<ONE_TIME_ITEM_CATEGORY extends string, SUBSCRIPTION_ITEM_CATEGORY extends string> {
    private readonly storeService: StoreService<ONE_TIME_ITEM_CATEGORY | SUBSCRIPTION_ITEM_CATEGORY>;
    private readonly paymentService: PaymentService<ONE_TIME_ITEM_CATEGORY, SUBSCRIPTION_ITEM_CATEGORY>;
    private readonly enabledProviders: PaymentProvider[];

    constructor(
        enabledProviders: PaymentProvider[],
        itemTypeToItemService: Map<ItemType, ItemCollectionService<ONE_TIME_ITEM_CATEGORY | SUBSCRIPTION_ITEM_CATEGORY>>,
        subHandlers: Map<SUBSCRIPTION_ITEM_CATEGORY, SubscriptionPaymentHandler<SUBSCRIPTION_ITEM_CATEGORY>>,
        oneTimeHandlers: Map<ONE_TIME_ITEM_CATEGORY, OneTimePaymentHandler<ONE_TIME_ITEM_CATEGORY>>
    ) {
        this.storeService = new StoreService(itemTypeToItemService);
        this.paymentService = new PaymentService(enabledProviders);
        this.enabledProviders = enabledProviders;

        // Register handlers
        for (const [category, handler] of subHandlers.entries()) {
            this.paymentService.registerSubscriptionHandler(category, handler);
        }
        for (const [category, handler] of oneTimeHandlers.entries()) {
            this.paymentService.registerOneTimeHandler(category, handler);
        }
    }

    private checkServiceEnabled(provider: PaymentProvider): void {
        if (!this.enabledProviders.includes(provider)) {
            throw new ServiceNotEnabledError(`${provider} service is not enabled.`);
        }
    }

    public async getOrdersByUserId(userId: string): Promise<PurchaseDetail[]> {
        return this.storeService.getOrdersByUserId(userId);
    }

    public async getItems(itemType: ItemType): Promise<AvailableItem[]> {
        return this.storeService.getAllItemsByType(itemType);
    }

    public async getAllItems(): Promise<Record<ItemType, AvailableItem[]>> {
        return this.storeService.getAllItems();
    }

    public async getPurchaseType(itemName: string): Promise<ItemType> {
        return this.storeService.getPurchaseType(itemName);
    }

    public async handleOneTimePayment(
        provider: PaymentProvider,
        paymentData: OneTimePaymentData<ONE_TIME_ITEM_CATEGORY>
    ): Promise<void> {
        this.checkServiceEnabled(provider);
        await this.paymentService.handleOneTimePayment(provider, paymentData.itemCategory, paymentData);
    }

    public async handleSubscription(
        provider: PaymentProvider,
        paymentData: SubscriptionPaymentData<SUBSCRIPTION_ITEM_CATEGORY>
    ): Promise<void> {
        this.checkServiceEnabled(provider);
        await this.paymentService.handleSubscriptionPayment(provider, paymentData.itemCategory, paymentData);
    }

    public async changeOrderStatus(orderId: string, status: PurchaseStatus): Promise<void> {
        await this.storeService.updateOrderStatus(orderId, status);
    }
} 