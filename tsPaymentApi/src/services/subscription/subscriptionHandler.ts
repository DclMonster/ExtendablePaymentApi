export interface SubscriptionHandler<T> {
    onSubscription(subscription: T): void;
} 