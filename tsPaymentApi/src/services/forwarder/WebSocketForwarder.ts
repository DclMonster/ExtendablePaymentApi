import WebSocket from 'ws';
import { SingleForwarder } from '../../../../../../../tsPaymentApi/src/services/forwarder/Forwarder';
import { PurchaseStatus } from '../types/PurchaseStatus';

export class WebSocketForwarder extends SingleForwarder {
    private websocket: WebSocket | null = null;
    private readonly url: string;

    constructor(url: string = 'ws://localhost:8765') {
        super(PurchaseStatus.SENT_TO_WEBSOCKET);
        this.url = url;
    }

    private async connect(): Promise<void> {
        return new Promise((resolve, reject) => {
            this.websocket = new WebSocket(this.url);
            this.websocket.on('open', () => resolve());
            this.websocket.on('error', (error) => reject(error));
        });
    }

    protected async onForwardEvent(eventData: Record<string, any>): Promise<void> {
        if (!this.websocket || this.websocket.readyState !== WebSocket.OPEN) {
            await this.connect();
        }

        if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
            return new Promise((resolve, reject) => {
                this.websocket!.send(JSON.stringify(eventData), (error) => {
                    if (error) {
                        reject(error);
                    } else {
                        resolve();
                    }
                });
            });
        } else {
            throw new Error('Failed to establish WebSocket connection');
        }
    }
} 