import { IncomingHttpHeaders } from 'http';
import { SignatureVerifier } from './abstract/SignatureVerifier';
import jwt from 'jsonwebtoken';
import axios from 'axios';
import { Logger } from '../utils/Logger';
import { VerifyResponse, OrderSchema, SubscriptionSchema } from '../interfaces/payment/verify';

interface AppleWebhookData {
    transactionId: string;
    [key: string]: any;
}

interface AppleVerifyReceiptResponse {
    status: number;
    environment: string;
    receipt: {
        bundle_id: string;
        application_version: string;
        original_purchase_date_ms: string;
        in_app: Array<{
            quantity: string;
            product_id: string;
            transaction_id: string;
            original_transaction_id: string;
            purchase_date_ms: string;
            expires_date_ms?: string;
            cancellation_date_ms?: string;
            is_trial_period: string;
            is_in_intro_offer_period: string;
        }>;
    };
    latest_receipt_info?: Array<{
        quantity: string;
        product_id: string;
        transaction_id: string;
        original_transaction_id: string;
        purchase_date_ms: string;
        expires_date_ms?: string;
        cancellation_date_ms?: string;
        is_trial_period: string;
        is_in_intro_offer_period: string;
    }>;
}

/**
 * Verifier class for Apple App Store webhook signatures and receipt verification.
 * Supports both production and sandbox environments.
 */
export class AppleVerifier extends SignatureVerifier {
    private readonly productionUrl = 'https://buy.itunes.apple.com/verifyReceipt';
    private readonly sandboxUrl = 'https://sandbox.itunes.apple.com/verifyReceipt';
    private readonly cache: Map<string, { data: any; timestamp: number }>;
    private readonly cacheDuration: number = 3600; // 1 hour

    constructor() {
        super('APPLE_PUBLIC_KEY');
        this.cache = new Map();
    }

    protected async verifySignature(data: AppleWebhookData, signature: string): Promise<boolean> {
        try {
            jwt.verify(signature, this.secret, {
                algorithms: ['ES256'],
                audience: data.transactionId
            });
            return true;
        } catch (error) {
            if (error instanceof jwt.JsonWebTokenError || error instanceof jwt.TokenExpiredError) {
                Logger.error('Signature verification error:', error);
                return false;
            }
            throw error;
        }
    }

    protected getSignatureFromHeader(headers: IncomingHttpHeaders): string {
        const signature = headers['x-apple-signature'];
        if (!signature || Array.isArray(signature)) {
            throw new Error('Invalid or missing Apple signature in headers');
        }
        return signature;
    }

    /**
     * Verify an App Store receipt
     * @param receiptData - The base64 encoded receipt data
     * @param isSandbox - Whether to use sandbox environment
     * @returns Verification result
     */
    public async verifyReceipt(receiptData: string, isSandbox: boolean = false): Promise<VerifyResponse> {
        try {
            const cacheKey = `receipt_${receiptData}`;
            const cached = this.getCachedData(cacheKey);
            if (cached) return cached;

            const verifyUrl = isSandbox ? this.sandboxUrl : this.productionUrl;
            const response = await axios.post<AppleVerifyReceiptResponse>(verifyUrl, {
                'receipt-data': receiptData,
                'exclude-old-transactions': true
            });

            // Handle sandbox response in production
            if (response.data.status === 21007 && !isSandbox) {
                return this.verifyReceipt(receiptData, true);
            }

            if (response.data.status !== 0) {
                throw new Error(`Receipt verification failed with status ${response.data.status}`);
            }

            const latestTransaction = response.data.latest_receipt_info?.[0] || response.data.receipt.in_app[0];
            const isSubscription = !!latestTransaction.expires_date_ms;

            if (isSubscription) {
                const subscriptionData: SubscriptionSchema = {
                    productId: latestTransaction.product_id,
                    transactionId: latestTransaction.transaction_id,
                    startDate: latestTransaction.purchase_date_ms,
                    expiresDate: latestTransaction.expires_date_ms,
                    subscriptionGroupIdentifier: null,
                    renewable: !latestTransaction.cancellation_date_ms,
                    status: latestTransaction.cancellation_date_ms ? 'cancelled' : 'active'
                };

                const result: VerifyResponse = {
                    status: 'success',
                    error: null,
                    type: 'subscription',
                    item: null,
                    subscription: subscriptionData,
                    state: null,
                    purchaseToken: null
                };

                this.setCachedData(cacheKey, result);
                return result;
            } else {
                const orderData: OrderSchema = {
                    productId: latestTransaction.product_id,
                    transactionId: latestTransaction.transaction_id,
                    purchaseDate: latestTransaction.purchase_date_ms,
                    qty: parseInt(latestTransaction.quantity, 10),
                    refundableQty: latestTransaction.cancellation_date_ms ? 0 : parseInt(latestTransaction.quantity, 10)
                };

                const result: VerifyResponse = {
                    status: 'success',
                    error: null,
                    type: 'product',
                    item: orderData,
                    subscription: null,
                    state: latestTransaction.cancellation_date_ms ? 'cancelled' : 'purchased',
                    purchaseToken: null
                };

                this.setCachedData(cacheKey, result);
                return result;
            }
        } catch (error) {
            Logger.error('Receipt verification error:', error);
            return {
                status: 'error',
                error: { msg: error.message },
                type: 'unknown',
                item: null,
                subscription: null,
                state: null,
                purchaseToken: null
            };
        }
    }

    private getCachedData(key: string): any | null {
        const cached = this.cache.get(key);
        if (cached && this.isCacheValid(cached.timestamp)) {
            return cached.data;
        }
        return null;
    }

    private setCachedData(key: string, data: any): void {
        this.cache.set(key, {
            data,
            timestamp: Date.now()
        });
    }

    private isCacheValid(timestamp: number): boolean {
        return (Date.now() - timestamp) < (this.cacheDuration * 1000);
    }

    /**
     * Clear the API response cache
     */
    public clearCache(): void {
        this.cache.clear();
    }
} 