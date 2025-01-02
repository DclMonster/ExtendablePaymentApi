import { PaymentProvider } from '../enums';
import { PaymentHandler } from './payment/paymentHandler';
import { AvailableItem } from './payment/availableItem';

interface PaymentData {
    transaction_id: string;
    amount: number;
    currency: string;
    status: string;
}

export class PaymentService {
    private applePaymentHandlers: PaymentHandler<PaymentData>[] = [];
    private googlePaymentHandlers: PaymentHandler<PaymentData>[] = [];
    private coinbasePaymentHandlers: PaymentHandler<PaymentData>[] = [];
    private paypalPaymentHandlers: PaymentHandler<PaymentData>[] = [];
    private coinsubPaymentHandlers: PaymentHandler<PaymentData>[] = [];

    registerPaymentHandler(provider: PaymentProvider, handler: PaymentHandler<PaymentData>) {
        switch (provider) {
            case PaymentProvider.APPLE:
                this.applePaymentHandlers.push(handler);
                break;
            case PaymentProvider.GOOGLE:
                this.googlePaymentHandlers.push(handler);
                break;
            case PaymentProvider.COINBASE:
                this.coinbasePaymentHandlers.push(handler);
                break;
            case PaymentProvider.PAYPAL:
                this.paypalPaymentHandlers.push(handler);
                break;
            case PaymentProvider.COINSUB:
                this.coinsubPaymentHandlers.push(handler);
                break;
        }
    }

    onPayment(provider: PaymentProvider, payment: PaymentData) {
        let handlers: PaymentHandler<PaymentData>[] = [];
        switch (provider) {
            case PaymentProvider.APPLE:
                handlers = this.applePaymentHandlers;
                break;
            case PaymentProvider.GOOGLE:
                handlers = this.googlePaymentHandlers;
                break;
            case PaymentProvider.COINBASE:
                handlers = this.coinbasePaymentHandlers;
                break;
            case PaymentProvider.PAYPAL:
                handlers = this.paypalPaymentHandlers;
                break;
            case PaymentProvider.COINSUB:
                handlers = this.coinsubPaymentHandlers;
                break;
        }
        handlers.forEach(handler => handler.onPayment(payment));
    }

    getItems(): Record<string, AvailableItem[]> {
        const result: Record<string, AvailableItem[]> = {};
        result[PaymentProvider.APPLE] = this.applePaymentHandlers.flatMap(handler => handler.getItems());
        result[PaymentProvider.GOOGLE] = this.googlePaymentHandlers.flatMap(handler => handler.getItems());
        result[PaymentProvider.COINBASE] = this.coinbasePaymentHandlers.flatMap(handler => handler.getItems());
        result[PaymentProvider.PAYPAL] = this.paypalPaymentHandlers.flatMap(handler => handler.getItems());
        result[PaymentProvider.COINSUB] = this.coinsubPaymentHandlers.flatMap(handler => handler.getItems());
        return result;
    }
} 