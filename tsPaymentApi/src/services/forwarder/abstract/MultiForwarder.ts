import { Forwarder } from './Forwarder';

export abstract class MultiForwarder<T extends string> implements Forwarder {
    protected forwarders: Map<T, Forwarder>;

    constructor(forwarders: Map<T, Forwarder>) {
        this.forwarders = forwarders;
    }

    public async forwardEvent(eventData: Record<string, any>): Promise<void> {
        const apiType = this.getApiType(eventData);
        const forwarder = this.forwarders.get(apiType);
        
        if (!forwarder) {
            throw new Error(`No forwarder found for API type: ${apiType}`);
        }

        await forwarder.forwardEvent(eventData);
    }

    protected abstract getApiType(eventData: Record<string, any>): T;
} 