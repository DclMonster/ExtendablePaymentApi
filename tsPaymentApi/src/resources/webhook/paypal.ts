import { Request, Response } from 'express';
import { providerSubscriptionService, paymentService } from '../services';
import { PaymentProvider } from '../enums';
import { paypalVerifier } from '../verifiers';
import { PaypalSubscriptionData, PaypalData } from '../services/payment_service';

export class PaypalWebhook {
    post(req: Request, res: Response): void {
        const eventData = req.body;

        const signature = req.headers['paypal-signature'] as string;

        if (!paypalVerifier.verifySignature(JSON.stringify(eventData), signature)) {
            res.status(400).json({ status: 'error', message: 'Invalid signature' });
            return;
        }

        const isOneTimePayment = paymentService.getItems().hasOwnProperty(PaymentProvider.PAYPAL);

        this.processEvent(eventData, isOneTimePayment);
        res.status(200).json({ status: 'success' });
    }

    private processEvent(eventData: any, isOneTimePayment: boolean): void {
        console.log("Received PayPal event:", eventData);
        const parsedData = this.parseEventData(eventData);
        if (isOneTimePayment) {
            paymentService.onPaypalPayment({
                transaction_id: parsedData.transaction_id || "",
                amount: parsedData.amount || 0.0,
                currency: parsedData.currency || "",
                status: parsedData.status || ""
            });
        } else {
            providerSubscriptionService.addSubscription({
                provider: PaymentProvider.PAYPAL,
                user_id: parsedData.user_id || "",
                subscription_data: parsedData
            });
        }
    }

    private parseEventData(eventData: any): any {
        return {
            transaction_id: eventData.transactionId,
            amount: eventData.amount,
            currency: eventData.currency,
            status: eventData.status
        };
    }
} 