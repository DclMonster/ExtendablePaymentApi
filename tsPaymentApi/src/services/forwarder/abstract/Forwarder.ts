export interface Forwarder {
    forwardEvent(eventData: string): Promise<void>;
} 