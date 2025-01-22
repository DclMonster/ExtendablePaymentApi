import { ItemType } from '../ItemType';
import { AvailableItem } from './AvailableItem';
import { PurchaseDetail } from './payment/PurchaseDetail';
import { PurchaseStatus } from './payment/PurchaseStatus';
import { ItemCollectionService } from './payment/abstract/ItemCollectionService';

export class StoreServiceError extends Error {
    constructor(message: string) {
        super(message);
        this.name = 'StoreServiceError';
    }
}

export class StoreService<ITEM_CATEGORY extends string> {
    private readonly itemTypeToItemService: Map<ItemType, ItemCollectionService<ITEM_CATEGORY>>;

    constructor(itemTypeToItemService: Map<ItemType, ItemCollectionService<ITEM_CATEGORY>>) {
        this.itemTypeToItemService = itemTypeToItemService;
    }

    public async getOrdersByUserId(userId: string): Promise<PurchaseDetail[]> {
        // TODO: Implement order retrieval from database
        return [];
    }

    public async getAllItemsByType(itemType: ItemType): Promise<AvailableItem[]> {
        const service = this.itemTypeToItemService.get(itemType);
        if (!service) {
            throw new StoreServiceError(`No service registered for item type: ${itemType}`);
        }
        return service.getItems();
    }

    public async getAllItems(): Promise<Record<ItemType, AvailableItem[]>> {
        const result: Record<ItemType, AvailableItem[]> = {} as Record<ItemType, AvailableItem[]>;
        for (const [type, service] of this.itemTypeToItemService.entries()) {
            result[type] = await service.getItems();
        }
        return result;
    }

    public async getPurchaseType(itemName: string): Promise<ItemType> {
        for (const [type, service] of this.itemTypeToItemService.entries()) {
            if (await service.validateItem(itemName)) {
                return type;
            }
        }
        throw new StoreServiceError(`No service found for item: ${itemName}`);
    }

    public async updateOrderStatus(orderId: string, status: PurchaseStatus): Promise<void> {
        // TODO: Implement order status update in database
    }
} 