import { IncomingHttpHeaders } from 'http';
import { SignatureVerifier } from './abstract/SignatureVerifier';
import crypto from 'crypto';

export class CoinsubVerifier extends SignatureVerifier {
    constructor() {
        super('COINSUB_SECRET');
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
        const signature = headers['coinsub-signature'];
        if (!signature || Array.isArray(signature)) {
            throw new Error('Invalid or missing CoinSub signature in headers');
        }
        return signature;
    }
} 