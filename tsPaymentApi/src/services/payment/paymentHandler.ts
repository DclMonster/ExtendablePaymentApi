import { AvailableItem } from './availableItem';

export interface PaymentHandler<T> {
    onPayment(payment: T): void;
    getItems(): AvailableItem[];
} 