import { IncomingHttpHeaders } from 'http';
import { SignatureVerifier } from './abstract/SignatureVerifier';
import crypto from 'crypto';

export class CoinbaseVerifier extends SignatureVerifier {
    constructor() {
        super('COINBASE_SECRET');
    }

    protected async verifySignature(data: Record<string, any>, signature: string): Promise<boolean> {
        try {
            const computedSignature = crypto
                .createHmac('sha256', this.secret)
                .update(JSON.stringify(data))
                .digest('hex');

            // Use timing-safe comparison
            return crypto.timingSafeEqual(
                Buffer.from(computedSignature),
                Buffer.from(signature)
            );
        } catch (error) {
            console.error('Signature verification failed:', error);
            return false;
        }
    }

    protected getSignatureFromHeader(headers: IncomingHttpHeaders): string {
        const signature = headers['cb-signature'];
        if (!signature || Array.isArray(signature)) {
            throw new Error('Invalid or missing Coinbase signature in headers');
        }
        return signature;
    }
} 