import { BasePaymentData } from './BasePaymentData';
import { OneTimePaymentData } from '../one_time/OneTimePaymentData';
import { SubscriptionPaymentData } from '../subscription/SubscriptionPaymentData';

export interface PaymentHandler<ITEM_CATEGORY extends string, T extends BasePaymentData<ITEM_CATEGORY>> {
    readonly category: ITEM_CATEGORY;
    handlePayment(paymentData: T): Promise<void>;
}

export interface OneTimePaymentHandler<ITEM_CATEGORY extends string> extends PaymentHandler<ITEM_CATEGORY, OneTimePaymentData<ITEM_CATEGORY>> {}

export interface SubscriptionPaymentHandler<ITEM_CATEGORY extends string> extends PaymentHandler<ITEM_CATEGORY, SubscriptionPaymentData<ITEM_CATEGORY>> {} 