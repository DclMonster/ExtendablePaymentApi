import { Request, Response, Router } from 'express';
import { SignatureVerifier } from '../../../verifiers/SignatureVerifier';
import { Forwarder } from '../../../services/forwarder/abstract/Forwarder';
import { OneTimePaymentData } from '../../../services/store/payment/one_time/OneTimePaymentData';
import { SubscriptionPaymentData } from '../../../services/store/payment/subscription/SubscriptionPaymentData';
import { PaymentProvider } from '../../../services/PaymentProvider';
import { ItemType } from '../../../services/ItemType';
import { Services } from '../../../services/Services';
import { getServices } from '../../../services';

export abstract class AbstractWebhook<PROVIDER_DATA, ITEM_CATEGORY extends string> {
    protected readonly _router: Router;
    private readonly verifier: SignatureVerifier;
    private readonly providerType: PaymentProvider;
    private readonly forwarder: Forwarder | null;
    private readonly services: Services;

    constructor(
        providerType: PaymentProvider,
        verifier: SignatureVerifier,
        forwarder: Forwarder | null = null
    ) {
        this._router = Router();
        this.verifier = verifier;
        this.providerType = providerType;
        this.forwarder = forwarder;
        this.services = getServices();

        // Set up POST route
        this._router.post('/', this.post.bind(this));
    }

    public get router(): Router {
        return this._router;
    }

    private async post(req: Request, res: Response): Promise<Response> {
        const data: string = req.body;
        const headers = req.headers;
        
        this.verifier.verifyHeaderSignature(headers, headers['x-signature'] as string);

        const providerData: PROVIDER_DATA = this.parseEventData(data);
        const itemPurchaseType: ItemType = this.getItemPurchaseType(providerData);

        if (this.forwarder) {
            await this.forwarder.forwardEvent(JSON.stringify(providerData));
        } else {
            switch (itemPurchaseType) {
                case ItemType.ONE_TIME_PAYMENT:
                    await this.services.handleOneTimePayment(
                        this.providerType,
                        this.getOneTimePaymentData(providerData)
                    );
                    break;
                case ItemType.SUBSCRIPTION:
                    await this.services.handleSubscription(
                        this.providerType,
                        this.getSubscriptionPaymentData(providerData)
                    );
                    break;
                case ItemType.UNKNOWN:
                    throw new Error(`Unknown item purchase type: ${itemPurchaseType}`);
            }
        }

        return res.status(200).send();
    }

    protected abstract getOneTimePaymentData(eventData: PROVIDER_DATA): OneTimePaymentData<ITEM_CATEGORY>;

    protected abstract getSubscriptionPaymentData(eventData: PROVIDER_DATA): SubscriptionPaymentData<ITEM_CATEGORY>;

    protected abstract itemNameProvider(eventData: PROVIDER_DATA): string;

    private getItemPurchaseType(eventData: PROVIDER_DATA): ItemType {
        return this.services.getPurchaseType(this.itemNameProvider(eventData));
    }

    protected abstract parseEventData(eventData: string): PROVIDER_DATA;
} 