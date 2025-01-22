import { SingleForwarder } from '../../../../../../../tsPaymentApi/src/services/forwarder/Forwarder';
import { PurchaseStatus } from '../types/PurchaseStatus';
import axios from 'axios';

export class ForwarderError extends Error {
    constructor(message: string) {
        super(message);
        this.name = 'ForwarderError';
    }
}

export class RestForwarder extends SingleForwarder {
    private readonly url: string;
    private readonly route: string;

    constructor(url: string) {
        super(PurchaseStatus.SENT_TO_PROCESSOR);
        this.url = url;
        this.route = process.env.ROUTE || '/creditor_api';
    }

    protected async onForwardEvent(eventData: Record<string, any>): Promise<void> {
        const fullUrl = `${this.url}${this.route}`;
        try {
            await axios.post(fullUrl, eventData, {
                headers: { 'Content-Type': 'application/json' }
            });
        } catch (error) {
            throw new ForwarderError(`Failed to forward event to ${fullUrl}: ${error}`);
        }
    }
} 