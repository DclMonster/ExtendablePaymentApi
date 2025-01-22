import { Request, Response, Router } from 'express';
import { getServices } from '../../services';

export class UserOrders {
    public readonly router: Router;

    constructor() {
        this.router = Router();
        this.router.get('/', this.get.bind(this));
    }

    private async get(req: Request, res: Response): Promise<void> {
        try {
            const userId = req.query.user_id;
            if (!userId || typeof userId !== 'string') {
                res.status(400).json({ error: 'User ID is required' });
                return;
            }

            const services = getServices();
            const orders = await services.getOrdersByUserId(userId);
            res.status(200).json({ orders });
        } catch (error) {
            res.status(500).json({ 
                error: 'Failed to retrieve user orders',
                details: error instanceof Error ? error.message : String(error)
            });
        }
    }
} 