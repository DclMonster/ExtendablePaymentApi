import { Request, Response } from 'express';
import { paymentService, appleSubscriptionService, coinbaseSubscriptionService, googleSubscriptionService } from '../services';

export class StoreItems {
    get(req: Request, res: Response): void {
        const result: any = {};
        result.items = paymentService.getItems();
        result.subscriptions = {
            apple: appleSubscriptionService.getItems(),
            coinbase: coinbaseSubscriptionService.getItems(),
            google: googleSubscriptionService.getItems()
        };
        res.status(200).json(result);
    }
} 