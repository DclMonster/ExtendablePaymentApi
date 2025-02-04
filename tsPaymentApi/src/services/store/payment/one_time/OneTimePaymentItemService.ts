import { ItemCollectionService } from '../abstract/ItemCollectionService';
import { ItemType } from '../../../../types/store';
import { AvailableItem } from '../../../../types/store/AvailableItem';

export class OneTimePaymentItemService<TCategory extends string> extends ItemCollectionService<TCategory> {
    constructor() {
        super(ItemType.ONE_TIME_PAYMENT, ItemType.ONE_TIME_PAYMENT);
    }

    async getItems(): Promise<AvailableItem[]> {
        // Implementation to be added
        return [];
    }

    async getItemByName(name: string): Promise<AvailableItem | null> {
        // Implementation to be added
        return null;
    }

    async validateItem(name: string): Promise<boolean> {
        // Implementation to be added
        return false;
    }
} 