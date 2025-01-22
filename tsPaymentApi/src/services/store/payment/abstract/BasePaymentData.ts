export interface BasePaymentData<ITEM_CATEGORY extends string> {
    itemName: string;
    itemCategory: ITEM_CATEGORY;
    purchaseId: string;
    userId: string;
    timeBought: string;
    status: string;
} 