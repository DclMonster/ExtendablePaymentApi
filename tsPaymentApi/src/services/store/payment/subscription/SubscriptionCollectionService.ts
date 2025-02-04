import { ItemCollectionService } from '../abstract/ItemCollectionService';
import { ItemType } from '../../../../types/store';

/**
 * Subscription collection service that matches the Python implementation.
 * Inherits all functionality from ItemCollectionService and only initializes
 * with ItemType.SUBSCRIPTION.
 */
export class SubscriptionCollectionService<TCategory extends string> extends ItemCollectionService<TCategory> {
    constructor() {
        super(ItemType.SUBSCRIPTION, ItemType.SUBSCRIPTION);
    }
} 