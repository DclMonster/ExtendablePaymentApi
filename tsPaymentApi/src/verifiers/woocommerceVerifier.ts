import { SignatureVerifier } from './abstract/signatureVerifier';
import axios from 'axios';
import crypto from 'crypto';
import { logger } from '../services/logger';

export class WooCommerceVerificationError extends Error {
    constructor(message: string) {
        super(message);
        this.name = 'WooCommerceVerificationError';
    }
}

interface WooCommerceConfig {
    consumerKey: string;
    consumerSecret: string;
    webhookSecret: string;
    apiUrl: string;
}

interface VerifyResponse {
    status: 'success' | 'error';
    order?: any;
    subscription?: any;
    error?: {
        msg: string;
    };
}

interface NotificationResponse {
    status: 'action_update' | 'error';
    type: string;
    update_body: Record<string, any>;
    identifier: Record<string, any> | null;
}

export class WooCommerceVerifier extends SignatureVerifier {
    private config: WooCommerceConfig;

    constructor() {
        super('WOOCOMMERCE_WEBHOOK_SECRET');
        
        this.config = {
            consumerKey: process.env.WOOCOMMERCE_CONSUMER_KEY!,
            consumerSecret: process.env.WOOCOMMERCE_CONSUMER_SECRET!,
            webhookSecret: process.env.WOOCOMMERCE_WEBHOOK_SECRET!,
            apiUrl: process.env.WOOCOMMERCE_API_URL!
        };

        if (!this.config.consumerKey || !this.config.consumerSecret || !this.config.webhookSecret) {
            throw new Error('Missing required WooCommerce configuration');
        }
    }

    public async verifySignature(payload: string, signature: string): Promise<boolean> {
        try {
            const hmac = crypto.createHmac('sha256', this.config.webhookSecret);
            const calculatedSignature = hmac.update(payload).digest('hex');
            return crypto.timingSafeEqual(
                Buffer.from(calculatedSignature),
                Buffer.from(signature)
            );
        } catch (error) {
            logger.error('WooCommerce signature verification error:', error);
            return false;
        }
    }

    public async verifyOrder(orderId: string, orderKey?: string): Promise<VerifyResponse> {
        try {
            const endpoint = `${this.config.apiUrl}/wp-json/wc/v3/orders/${orderId}`;
            const params = orderKey ? { order_key: orderKey } : {};

            const response = await axios.get(endpoint, {
                auth: {
                    username: this.config.consumerKey,
                    password: this.config.consumerSecret
                },
                params
            });

            return {
                status: 'success',
                order: response.data
            };

        } catch (error) {
            logger.error('WooCommerce order verification error:', error);
            return {
                status: 'error',
                error: {
                    msg: error instanceof Error ? error.message : 'Unknown error'
                }
            };
        }
    }

    public async verifySubscription(subscriptionId: string): Promise<VerifyResponse> {
        try {
            const endpoint = `${this.config.apiUrl}/wp-json/wc/v3/subscriptions/${subscriptionId}`;

            const response = await axios.get(endpoint, {
                auth: {
                    username: this.config.consumerKey,
                    password: this.config.consumerSecret
                }
            });

            return {
                status: 'success',
                subscription: response.data
            };

        } catch (error) {
            logger.error('WooCommerce subscription verification error:', error);
            return {
                status: 'error',
                error: {
                    msg: error instanceof Error ? error.message : 'Unknown error'
                }
            };
        }
    }

    public async handleNotification(payload: Record<string, any>): Promise<NotificationResponse> {
        try {
            const event = payload.webhook_event as string;
            
            if (event.startsWith('order.')) {
                return this.handleOrderNotification(payload);
            } else if (event.startsWith('subscription.')) {
                return event === 'subscription.cancelled' 
                    ? this.handleSubscriptionCancellation(payload)
                    : this.handleSubscriptionNotification(payload);
            }
            
            return {
                status: 'error',
                type: 'unknown_event',
                update_body: {},
                identifier: null
            };
            
        } catch (error) {
            logger.error('WooCommerce notification handling error:', error);
            return {
                status: 'error',
                type: 'processing_error',
                update_body: { error: error instanceof Error ? error.message : 'Unknown error' },
                identifier: null
            };
        }
    }

    private handleOrderNotification(payload: Record<string, any>): NotificationResponse {
        return {
            status: 'action_update',
            type: 'order_update',
            update_body: {
                status: payload.status,
                order_id: payload.id
            },
            identifier: {
                order_id: payload.id,
                product_id: payload.line_items?.[0]?.product_id
            }
        };
    }

    private handleSubscriptionNotification(payload: Record<string, any>): NotificationResponse {
        return {
            status: 'action_update',
            type: 'subscription_update',
            update_body: {
                status: 'active',
                subscription_id: payload.id
            },
            identifier: {
                subscription_id: payload.id,
                product_id: payload.line_items?.[0]?.product_id
            }
        };
    }

    private handleSubscriptionCancellation(payload: Record<string, any>): NotificationResponse {
        return {
            status: 'action_update',
            type: 'subscription_cancelled',
            update_body: {
                status: 'cancelled',
                subscription_id: payload.id
            },
            identifier: {
                subscription_id: payload.id,
                product_id: payload.line_items?.[0]?.product_id
            }
        };
    }
}

export const woocommerceVerifier = new WooCommerceVerifier(); 