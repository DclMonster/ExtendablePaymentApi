import { BasePaymentData } from '../abstract/BasePaymentData';

export interface SubscriptionPaymentData<ITEM_CATEGORY extends string> extends BasePaymentData<ITEM_CATEGORY> {} 