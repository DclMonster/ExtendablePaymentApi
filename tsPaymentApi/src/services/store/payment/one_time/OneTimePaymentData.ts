import { BasePaymentData } from '../abstract/PaymentHandler';

export interface OneTimePaymentData<TCategory extends string> extends BasePaymentData<TCategory> {
    status: 'paid' | 'webhook_recieved' | 'sent_to_websocket' | 'sent_to_processor';
} 