import { BasePaymentData } from '../abstract/BasePaymentData';

export interface OneTimePaymentData<ITEM_CATEGORY extends string> extends BasePaymentData<ITEM_CATEGORY> {
    quantity: number;
} 