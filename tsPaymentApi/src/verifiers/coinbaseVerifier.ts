import axios from 'axios';
import crypto from 'crypto';
import { SignatureVerifier } from './abstract/SignatureVerifier';
import { Logger } from '../utils/Logger';

interface CoinbaseCharge {
    id: string;
    name: string;
    description: string;
    pricing_type: 'fixed_price' | 'no_price';
    local_price: {
        amount: string;
        currency: string;
    };
    metadata?: Record<string, any>;
}

interface CoinbaseChargeResponse {
    data: CoinbaseCharge;
}

interface CoinbaseChargeListResponse {
    data: CoinbaseCharge[];
    pagination: {
        cursor: string;
        has_more: boolean;
    };
}

export class CoinbaseVerifier extends SignatureVerifier {
    private static readonly COMMERCE_API = 'https://api.commerce.coinbase.com';
    private static readonly CERT_CACHE: Map<string, string> = new Map();

    private readonly apiKey: string;
    private readonly sandboxMode: boolean;

    constructor() {
        super('COINBASE_SECRET');
        
        const apiKey = process.env.COINBASE_API_KEY;
        if (!apiKey) {
            throw new Error('COINBASE_API_KEY not set in environment variables');
        }
        
        this.apiKey = apiKey;
        this.sandboxMode = process.env.COINBASE_SANDBOX_MODE?.toLowerCase() === 'true';
    }

    public verifySignature(data: Record<string, any>, signature: string): boolean {
        try {
            // Create HMAC signature using the shared secret
            const computedSignature = crypto
                .createHmac('sha256', this.secret)
                .update(JSON.stringify(data))
                .digest('hex');
            
            // Use constant-time comparison to prevent timing attacks
            return crypto.timingSafeEqual(
                Buffer.from(computedSignature),
                Buffer.from(signature)
            );
        } catch (error) {
            Logger.error('Signature verification failed:', error);
            return false;
        }
    }

    public getSignatureFromHeader(header: Record<string, any>): string {
        const signature = header['x-cc-webhook-signature'];
        if (!signature) {
            throw new Error('Missing Coinbase signature in headers');
        }
        if (typeof signature !== 'string') {
            throw new Error('Invalid Coinbase signature format');
        }
        return signature;
    }

    public async verifyCharge(chargeId: string): Promise<CoinbaseCharge> {
        try {
            const response = await axios.get<CoinbaseChargeResponse>(
                `${CoinbaseVerifier.COMMERCE_API}/charges/${chargeId}`,
                { headers: this.getAuthHeaders() }
            );
            
            return response.data.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(`Charge verification failed: ${error.response?.data || error.message}`);
            }
            throw new Error(`Charge verification error: ${error}`);
        }
    }

    public async createCharge(chargeData: Partial<CoinbaseCharge>): Promise<CoinbaseCharge> {
        try {
            const response = await axios.post<CoinbaseChargeResponse>(
                `${CoinbaseVerifier.COMMERCE_API}/charges`,
                chargeData,
                { headers: this.getAuthHeaders() }
            );
            
            return response.data.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(`Charge creation failed: ${error.response?.data || error.message}`);
            }
            throw new Error(`Charge creation error: ${error}`);
        }
    }

    public async listCharges(limit: number = 25, startingAfter?: string): Promise<CoinbaseChargeListResponse> {
        try {
            const params = new URLSearchParams({
                limit: Math.min(limit, 100).toString()
            });
            
            if (startingAfter) {
                params.append('starting_after', startingAfter);
            }
            
            const response = await axios.get<CoinbaseChargeListResponse>(
                `${CoinbaseVerifier.COMMERCE_API}/charges?${params.toString()}`,
                { headers: this.getAuthHeaders() }
            );
            
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(`Listing charges failed: ${error.response?.data || error.message}`);
            }
            throw new Error(`Listing charges error: ${error}`);
        }
    }

    private getAuthHeaders(): Record<string, string> {
        return {
            'X-CC-Api-Key': this.apiKey,
            'X-CC-Version': '2018-03-22',
            'Content-Type': 'application/json'
        };
    }
} 