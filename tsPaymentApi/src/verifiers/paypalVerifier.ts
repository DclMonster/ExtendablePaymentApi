import axios from 'axios';
import crypto from 'crypto';
import { SignatureVerifier } from './abstract/SignatureVerifier';
import { Logger } from '../utils/Logger';

interface PayPalAccessToken {
    access_token: string;
    token_type: string;
    expires_in: number;
}

interface PayPalOrder {
    id: string;
    status: string;
    intent: string;
    purchase_units: Array<{
        amount: {
            currency_code: string;
            value: string;
        };
        reference_id?: string;
        custom_id?: string;
        description?: string;
    }>;
    create_time: string;
    update_time: string;
    payer?: {
        email_address?: string;
        payer_id?: string;
    };
}

interface PayPalSubscription {
    id: string;
    status: string;
    plan_id: string;
    start_time: string;
    quantity: string;
    subscriber: {
        email_address?: string;
        payer_id: string;
    };
    billing_info: {
        outstanding_balance: {
            currency_code: string;
            value: string;
        };
        cycle_executions: Array<{
            tenure_type: string;
            sequence: number;
            cycles_completed: number;
            cycles_remaining: number;
            current_pricing_scheme_version: number;
        }>;
        last_payment: {
            amount: {
                currency_code: string;
                value: string;
            };
            time: string;
        };
        next_billing_time: string;
        failed_payments_count: number;
    };
}

export class PayPalVerifier extends SignatureVerifier {
    private static readonly SANDBOX_API = 'https://api-m.sandbox.paypal.com';
    private static readonly LIVE_API = 'https://api-m.paypal.com';
    private static readonly TOKEN_CACHE = new Map<string, { token: string; expires: number }>();

    private readonly clientId: string;
    private readonly clientSecret: string;
    private readonly webhookId: string;
    private readonly sandboxMode: boolean;

    constructor() {
        super('PAYPAL_WEBHOOK_SECRET');
        
        const clientId = process.env.PAYPAL_CLIENT_ID;
        const clientSecret = process.env.PAYPAL_CLIENT_SECRET;
        const webhookId = process.env.PAYPAL_WEBHOOK_ID;
        
        if (!clientId || !clientSecret || !webhookId) {
            throw new Error('Missing required PayPal environment variables');
        }
        
        this.clientId = clientId;
        this.clientSecret = clientSecret;
        this.webhookId = webhookId;
        this.sandboxMode = process.env.PAYPAL_SANDBOX_MODE?.toLowerCase() === 'true';
    }

    public verifySignature(data: Record<string, any>, signature: string): boolean {
        try {
            const webhookEvent = {
                auth_algo: data.auth_algo,
                cert_url: data.cert_url,
                transmission_id: data.transmission_id,
                transmission_sig: signature,
                transmission_time: data.transmission_time,
                webhook_id: this.webhookId,
                webhook_event: data.webhook_event
            };

            // Create CRC32 hash of the webhook event
            const crc32 = this.calculateCRC32(JSON.stringify(webhookEvent));
            
            // Verify the signature using the webhook secret
            const computedSignature = crypto
                .createHmac('sha256', this.secret)
                .update(crc32)
                .digest('hex');
            
            return crypto.timingSafeEqual(
                Buffer.from(computedSignature),
                Buffer.from(signature)
            );
        } catch (error) {
            Logger.error('PayPal signature verification failed:', error);
            return false;
        }
    }

    public getSignatureFromHeader(header: Record<string, any>): string {
        const signature = header['paypal-transmission-sig'];
        if (!signature) {
            throw new Error('Missing PayPal signature in headers');
        }
        if (typeof signature !== 'string') {
            throw new Error('Invalid PayPal signature format');
        }
        return signature;
    }

    public async verifyOrder(orderId: string): Promise<PayPalOrder> {
        try {
            const token = await this.getAccessToken();
            const response = await axios.get<PayPalOrder>(
                `${this.getApiUrl()}/v2/checkout/orders/${orderId}`,
                {
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    }
                }
            );
            
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(`Order verification failed: ${error.response?.data || error.message}`);
            }
            throw new Error(`Order verification error: ${error}`);
        }
    }

    public async verifySubscription(subscriptionId: string): Promise<PayPalSubscription> {
        try {
            const token = await this.getAccessToken();
            const response = await axios.get<PayPalSubscription>(
                `${this.getApiUrl()}/v1/billing/subscriptions/${subscriptionId}`,
                {
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    }
                }
            );
            
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(`Subscription verification failed: ${error.response?.data || error.message}`);
            }
            throw new Error(`Subscription verification error: ${error}`);
        }
    }

    private async getAccessToken(): Promise<string> {
        const cacheKey = `${this.clientId}:${this.sandboxMode}`;
        const cached = PayPalVerifier.TOKEN_CACHE.get(cacheKey);
        
        if (cached && cached.expires > Date.now()) {
            return cached.token;
        }
        
        try {
            const auth = Buffer.from(`${this.clientId}:${this.clientSecret}`).toString('base64');
            const response = await axios.post<PayPalAccessToken>(
                `${this.getApiUrl()}/v1/oauth2/token`,
                'grant_type=client_credentials',
                {
                    headers: {
                        'Authorization': `Basic ${auth}`,
                        'Content-Type': 'application/x-www-form-urlencoded'
                    }
                }
            );
            
            const { access_token, expires_in } = response.data;
            PayPalVerifier.TOKEN_CACHE.set(cacheKey, {
                token: access_token,
                expires: Date.now() + (expires_in * 1000) - 60000 // Expire 1 minute early
            });
            
            return access_token;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(`Failed to get access token: ${error.response?.data || error.message}`);
            }
            throw new Error(`Access token error: ${error}`);
        }
    }

    private getApiUrl(): string {
        return this.sandboxMode ? PayPalVerifier.SANDBOX_API : PayPalVerifier.LIVE_API;
    }

    private calculateCRC32(str: string): string {
        let crc = 0 ^ (-1);
        for (let i = 0; i < str.length; i++) {
            crc = (crc >>> 8) ^ this.crc32Table[(crc ^ str.charCodeAt(i)) & 0xFF];
        }
        return (crc ^ (-1)) >>> 0;
    }

    private readonly crc32Table = new Uint32Array(256).map((_, i) => {
        let c = i;
        for (let j = 0; j < 8; j++) {
            c = ((c & 1) ? (0xEDB88320 ^ (c >>> 1)) : (c >>> 1));
        }
        return c;
    });
} 