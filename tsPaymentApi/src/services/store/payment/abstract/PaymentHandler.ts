import { ItemCollectionService } from './ItemCollectionService';

export interface BasePaymentData<TCategory extends string> {
    status: string;
    itemCategory: TCategory;
}

export abstract class PaymentHandler<TCategory extends string, TPaymentData extends BasePaymentData<TCategory>> {
    protected readonly category: TCategory;
    protected readonly logger?: ItemCollectionService<TCategory>;

    constructor(category: TCategory, logger?: ItemCollectionService<TCategory>) {
        this.category = category;
        this.logger = logger;
    }

    abstract onPayment(payment: TPaymentData): Promise<void>;
} 