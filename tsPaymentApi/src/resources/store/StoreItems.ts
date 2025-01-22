import { Request, Response, Router } from 'express';
import { getServices } from '../../services';

export class StoreItems {
    public readonly router: Router;

    constructor() {
        this.router = Router();
        this.router.get('/', this.get.bind(this));
    }

    private async get(_req: Request, res: Response): Promise<void> {
        try {
            const services = getServices();
            const items = await services.getAllItems();
            res.status(200).json({ items });
        } catch (error) {
            res.status(500).json({ 
                error: 'Failed to retrieve store items',
                details: error instanceof Error ? error.message : String(error)
            });
        }
    }
} 