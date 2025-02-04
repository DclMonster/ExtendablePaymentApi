import { PaymentHandler } from '../abstract/PaymentHandler';
import { ItemCollectionService } from '../abstract/ItemCollectionService';
import { OneTimePaymentData } from './OneTimePaymentData';

export class OneTimePaymentHandler<TCategory extends string> extends PaymentHandler<TCategory, OneTimePaymentData<TCategory>> {
    constructor(category: TCategory, logger?: ItemCollectionService<TCategory>) {
        super(category, logger);
    }

    public async onPayment(payment: OneTimePaymentData<TCategory>): Promise<void> {
        if (!['paid', 'webhook_recieved', 'sent_to_websocket', 'sent_to_processor'].includes(payment.status)) {
            throw new Error(`Invalid payment status: ${payment.status}`);
        }
        
        console.log(`Payment received for ${payment.itemCategory} item`);
    }
} 