import { AvailableItem } from '../../AvailableItem';

export interface ItemCollectionService<ITEM_CATEGORY extends string> {
    getItems(): Promise<AvailableItem[]>;
    getItemByName(name: string): Promise<AvailableItem | null>;
    validateItem(name: string): Promise<boolean>;
} 