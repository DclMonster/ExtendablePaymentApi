import { Request, Response } from 'express';
import { subscriptionService, paymentService } from '../../services';
import { PaymentProvider } from '../../enums';
import { googleVerifier } from '../../verifiers';

export class GoogleWebhook {
    post(req: Request, res: Response): void {
        const eventData = req.body;

        const jws = eventData.signedPayload;

        if (!googleVerifier.verifySignature(jws)) {
            res.status(400).json({ status: 'error', message: 'Invalid signature' });
            return;
        }

        const isOneTimePayment = paymentService.getItems().hasOwnProperty(PaymentProvider.GOOGLE);

        this.processEvent(eventData, isOneTimePayment);
        res.status(200).json({ status: 'success' });
    }

    private processEvent(eventData: any, isOneTimePayment: boolean): void {
        console.log("Received Google event:", eventData);
        const parsedData = this.parseEventData(eventData);
        if (isOneTimePayment) {
            paymentService.onPayment(PaymentProvider.GOOGLE, {
                transaction_id: parsedData.transaction_id || "",
                amount: parsedData.amount || 0.0,
                currency: parsedData.currency || "",
                status: parsedData.status || ""
            });
        } else {
            subscriptionService.addSubscription(PaymentProvider.GOOGLE, {
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