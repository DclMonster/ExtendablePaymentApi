import { Forwarder } from './Forwarder';
import { PurchaseStatus } from '../../../enums';
import { getServices } from '../../index';
import { Services } from '../../Services';

export abstract class SingleForwarder implements Forwarder {
    protected readonly service: Services;
    private readonly status: PurchaseStatus;

    constructor(status: PurchaseStatus) {
        this.service = getServices();
        this.status = status;
    }

    public async forwardEvent(eventData: Record<string, any>): Promise<void> {
        const orderId = String(eventData.order_id || '');
        
        if (this.service) {
            await this.service.changeOrderStatus(orderId, this.status);
        }
        
        await this.onForwardEvent(eventData);
    }

    protected abstract onForwardEvent(eventData: Record<string, any>): Promise<void>;
} 