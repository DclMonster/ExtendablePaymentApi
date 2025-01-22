import { PurchaseStatus } from './PurchaseStatus';

export interface PurchaseDetail {
    orderId: string;
    userId: string;
    itemName: string;
    itemCategory: string;
    quantity?: number;
    timeBought: string;
    status: PurchaseStatus;
    provider: string;
} 