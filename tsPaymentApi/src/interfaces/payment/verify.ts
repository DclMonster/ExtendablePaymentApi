/**
 * Schema for order data
 */
export interface OrderSchema {
    productId: string;
    transactionId: string;
    purchaseDate: string;
    qty: number;
    refundableQty?: number;
}

/**
 * Schema for subscription data
 */
export interface SubscriptionSchema {
    productId: string;
    transactionId: string;
    startDate: string;
    expiresDate?: string;
    subscriptionGroupIdentifier: string | null;
    renewable: boolean;
    status: string;
}

/**
 * Error response schema
 */
export interface ErrorResponse {
    msg: string;
    [key: string]: any;
}

/**
 * Verification response schema
 */
export interface VerifyResponse {
    status: 'success' | 'error';
    error: ErrorResponse | null;
    type: 'product' | 'subscription' | 'unknown';
    item: OrderSchema | null;
    subscription: SubscriptionSchema | null;
    state: string | null;
    purchaseToken: string | null;
} 