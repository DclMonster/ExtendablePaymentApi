import { IncomingHttpHeaders } from 'http';
import { SignatureVerifier } from './abstract/SignatureVerifier';
import jwt from 'jsonwebtoken';
import { google } from 'googleapis';
import { OAuth2Client } from 'google-auth-library';
import { Logger } from '../utils/Logger';
import { VerifyResponse, OrderSchema, SubscriptionSchema } from '../interfaces/payment/verify';
import { ProductType } from '../interfaces/payment/ProductType';

/**
 * Verifier class for Google Play webhook signatures and API integration.
 * Supports both production and sandbox environments.
 */
export class GoogleVerifier extends SignatureVerifier {
    private readonly packageName: string;
    private readonly service: any;
    private readonly cache: Map<string, { data: any; timestamp: number }>;
    private readonly cacheDuration: number = 3600; // 1 hour

    constructor() {
        super('GOOGLE_PUBLIC_KEY');
        this.packageName = process.env.GOOGLE_PACKAGE_NAME || '';
        this.cache = new Map();
        
        if (!this.packageName || !process.env.GOOGLE_SERVICE_ACCOUNT_KEY) {
            throw new Error('Missing required Google Play configuration');
        }

        this.initializeApiClient();
    }

    protected async verifySignature(data: Record<string, any>, signature: string): Promise<boolean> {
        try {
            jwt.verify(signature, this.secret, { algorithms: ['RS256'] });
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
        const signature = headers['signature'];
        if (!signature || Array.isArray(signature)) {
            throw new Error('Invalid or missing Google signature in headers');
        }
        return signature;
    }

    private initializeApiClient(): void {
        try {
            const auth = new google.auth.GoogleAuth({
                keyFile: process.env.GOOGLE_SERVICE_ACCOUNT_KEY,
                scopes: ['https://www.googleapis.com/auth/androidpublisher']
            });

            this.service = google.androidpublisher({
                version: 'v3',
                auth
            });
        } catch (error) {
            Logger.error('Failed to initialize Google Play API client:', error);
            throw new Error('API client initialization failed');
        }
    }

    /**
     * Verify a one-time purchase
     * @param purchaseToken - The purchase token to verify
     * @param productId - The product ID
     * @returns Verification result
     */
    public async verifyPurchase(purchaseToken: string, productId: string): Promise<VerifyResponse> {
        try {
            const cacheKey = `purchase_${productId}_${purchaseToken}`;
            const cached = this.getCachedData(cacheKey);
            if (cached) return cached;

            const response = await this.service.purchases.products.get({
                packageName: this.packageName,
                productId,
                token: purchaseToken
            });

            const orderData: OrderSchema = {
                productId,
                transactionId: response.data.orderId,
                purchaseDate: response.data.purchaseTimeMillis,
                qty: response.data.quantity || 1,
                refundableQty: response.data.refundableQuantity
            };

            const result: VerifyResponse = {
                status: 'success',
                error: null,
                type: 'product',
                item: orderData,
                subscription: null,
                state: response.data.purchaseState,
                purchaseToken
            };

            this.setCachedData(cacheKey, result);
            return result;
        } catch (error) {
            Logger.error('Purchase verification error:', error);
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

    /**
     * Verify a subscription purchase
     * @param purchaseToken - The purchase token to verify
     * @param subscriptionId - The subscription ID
     * @returns Verification result
     */
    public async verifySubscription(purchaseToken: string, subscriptionId: string): Promise<VerifyResponse> {
        try {
            const cacheKey = `subscription_${subscriptionId}_${purchaseToken}`;
            const cached = this.getCachedData(cacheKey);
            if (cached) return cached;

            const response = await this.service.purchases.subscriptionsv2.get({
                packageName: this.packageName,
                token: purchaseToken
            });

            const subscriptionData: SubscriptionSchema = {
                productId: subscriptionId,
                transactionId: response.data.orderId,
                startDate: response.data.startTimeMillis,
                expiresDate: response.data.expiryTimeMillis,
                subscriptionGroupIdentifier: null,
                renewable: response.data.autoRenewing || false,
                status: response.data.paymentState || 'unknown'
            };

            const result: VerifyResponse = {
                status: 'success',
                error: null,
                type: 'subscription',
                item: null,
                subscription: subscriptionData,
                state: null,
                purchaseToken
            };

            this.setCachedData(cacheKey, result);
            return result;
        } catch (error) {
            Logger.error('Subscription verification error:', error);
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

    /**
     * Get a list of voided purchases
     * @param startTime - Optional start time for the query (RFC3339 timestamp)
     * @returns List of voided purchases
     */
    public async getVoidedPurchases(startTime?: string): Promise<any[]> {
        try {
            const params: any = { packageName: this.packageName };
            if (startTime) params.startTime = startTime;

            const response = await this.service.purchases.voidedpurchases.list(params);
            return response.data.voidedPurchases || [];
        } catch (error) {
            Logger.error('Error retrieving voided purchases:', error);
            return [];
        }
    }

    /**
     * Acknowledge a purchase or subscription
     * @param purchaseToken - The purchase token to acknowledge
     * @param productId - The product ID
     * @param isSubscription - Whether this is a subscription acknowledgment
     * @returns Whether acknowledgment was successful
     */
    public async acknowledgePurchase(
        purchaseToken: string,
        productId: string,
        isSubscription: boolean = false
    ): Promise<boolean> {
        try {
            if (isSubscription) {
                await this.service.purchases.subscriptions.acknowledge({
                    packageName: this.packageName,
                    subscriptionId: productId,
                    token: purchaseToken
                });
            } else {
                await this.service.purchases.products.acknowledge({
                    packageName: this.packageName,
                    productId,
                    token: purchaseToken
                });
            }
            return true;
        } catch (error) {
            Logger.error('Purchase acknowledgment error:', error);
            return false;
        }
    }

    /**
     * Create a new in-app product
     * @param productData - Product details
     * @returns Created product details
     */
    public async createProduct(productData: {
        productId: string;
        name: string;
        description: string;
        priceMicros: number;
        type: ProductType;
    }): Promise<any> {
        try {
            const response = await this.service.inappproducts.insert({
                packageName: this.packageName,
                requestBody: {
                    packageName: this.packageName,
                    productId: productData.productId,
                    listing: {
                        title: productData.name,
                        description: productData.description
                    },
                    defaultPrice: {
                        priceMicros: productData.priceMicros.toString(),
                        currency: 'USD'
                    },
                    purchaseType: 'managedUser',
                    status: 'active'
                },
                autoConvertMissingPrices: true
            });

            Logger.info('Created product:', response.data);
            return response.data;
        } catch (error) {
            Logger.error('Error creating product:', error);
            throw new Error(`Product creation failed: ${error.message}`);
        }
    }

    /**
     * Create a new subscription
     * @param subscriptionData - Subscription details
     * @returns Created subscription details
     */
    public async createSubscription(subscriptionData: {
        subscriptionId: string;
        name: string;
        description: string;
        priceMicros: number;
        billingPeriod: string;
        gracePeriod?: string;
    }): Promise<any> {
        try {
            const response = await this.service.monetization.subscriptions.create({
                packageName: this.packageName,
                requestBody: {
                    packageName: this.packageName,
                    subscriptionId: subscriptionData.subscriptionId,
                    listing: {
                        title: subscriptionData.name,
                        description: subscriptionData.description
                    },
                    defaultPrice: {
                        priceMicros: subscriptionData.priceMicros.toString(),
                        currency: 'USD'
                    },
                    subscriptionPeriod: subscriptionData.billingPeriod,
                    gracePeriod: subscriptionData.gracePeriod || 'P0D',
                    status: 'active'
                }
            });

            Logger.info('Created subscription:', response.data);
            return response.data;
        } catch (error) {
            Logger.error('Error creating subscription:', error);
            throw new Error(`Subscription creation failed: ${error.message}`);
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