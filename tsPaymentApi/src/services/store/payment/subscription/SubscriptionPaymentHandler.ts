import { PaymentHandler } from '../abstract/PaymentHandler';
import { ItemCollectionService } from '../abstract/ItemCollectionService';
import { SubscriptionPaymentData } from './SubscriptionPaymentData';

export class SubscriptionPaymentHandler<TCategory extends string> extends PaymentHandler<TCategory, SubscriptionPaymentData<TCategory>> {
    constructor(category: TCategory, logger?: ItemCollectionService<TCategory>) {
        super(category, logger);
    }

    public async onPayment(payment: SubscriptionPaymentData<TCategory>): Promise<void> {
        if (!['paid', 'webhook_recieved', 'sent_to_websocket', 'sent_to_processor'].includes(payment.status)) {
            throw new Error(`Invalid payment status: ${payment.status}`);
        }
        
        console.log(`Payment received for ${payment.itemCategory} item`);
    }
} 