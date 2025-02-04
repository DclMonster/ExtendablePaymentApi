import { AvailableItem } from '../../../../types/store/AvailableItem';
import { ItemType } from '../../../../types/store';
import { PurchaseStatus } from '../../../../enums';

export interface PurchaseDetail {
    purchaseId: string;
    itemId: string;
    userId: string;
    timeBought: Date;
}

export interface PurchaseOrderStatus extends PurchaseDetail {
    status: PurchaseStatus;
}

export abstract class ItemCollectionService<TCategory extends string> {
    protected readonly itemType: ItemType;
    protected readonly category: TCategory;

    constructor(itemType: ItemType, category: TCategory) {
        this.itemType = itemType;
        this.category = category;
    }

    public getItem(itemCategory: TCategory, itemId: string): Promise<AvailableItem> {
        throw new Error('Not implemented');
    }

    public getAllItemsInCategory(itemCategory: TCategory): Promise<AvailableItem[]> {
        throw new Error('Not implemented');
    }

    public getAllItems(): Promise<AvailableItem[]> {
        throw new Error('Not implemented');
    }

    public getOrdersByUserId(userId: string): Promise<PurchaseDetail[]> {
        throw new Error('Not implemented');
    }

    public hasItem(itemName: string): Promise<boolean> {
        throw new Error('Not implemented');
    }

    public hasOrder(purchaseId: string): Promise<boolean> {
        throw new Error('Not implemented');
    }

    public logWebhookReceived(details: PurchaseDetail): Promise<void> {
        throw new Error('Not implemented');
    }

    public changeOrderStatus(purchaseId: string, status: PurchaseStatus): Promise<void> {
        throw new Error('Not implemented');
    }

    public get type(): ItemType {
        return this.itemType;
    }
} 