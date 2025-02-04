import { OneTimePaymentData } from '../../one_time/OneTimePaymentData';

export interface PayPalOneTimePaymentData<TCategory extends string> extends OneTimePaymentData<TCategory> {} 