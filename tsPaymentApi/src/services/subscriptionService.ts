import { PaymentProvider } from '../enums';
import { SubscriptionHandler } from './subscription/subscriptionHandler';

interface SubscriptionData {
    user_id: string;
    subscription_data: any;
}

export class SubscriptionService {
    private appleSubscriptionHandlers: SubscriptionHandler<SubscriptionData>[] = [];
    private googleSubscriptionHandlers: SubscriptionHandler<SubscriptionData>[] = [];
    private coinbaseSubscriptionHandlers: SubscriptionHandler<SubscriptionData>[] = [];

    registerSubscriptionHandler(provider: PaymentProvider, handler: SubscriptionHandler<SubscriptionData>) {
        switch (provider) {
            case PaymentProvider.APPLE:
                this.appleSubscriptionHandlers.push(handler);
                break;
            case PaymentProvider.GOOGLE:
                this.googleSubscriptionHandlers.push(handler);
                break;
            case PaymentProvider.COINBASE:
                this.coinbaseSubscriptionHandlers.push(handler);
                break;
        }
    }

    addSubscription(provider: PaymentProvider, subscription: SubscriptionData) {
        let handlers: SubscriptionHandler<SubscriptionData>[] = [];
        switch (provider) {
            case PaymentProvider.APPLE:
                handlers = this.appleSubscriptionHandlers;
                break;
            case PaymentProvider.GOOGLE:
                handlers = this.googleSubscriptionHandlers;
                break;
            case PaymentProvider.COINBASE:
                handlers = this.coinbaseSubscriptionHandlers;
                break;
        }
        handlers.forEach(handler => handler.onSubscription(subscription));
    }
} 