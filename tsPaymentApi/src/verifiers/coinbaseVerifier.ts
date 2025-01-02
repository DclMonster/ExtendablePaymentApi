import crypto from 'crypto';

export class CoinbaseVerifier {
    private secret: string;

    constructor(secret: string) {
        this.secret = secret;
    }

    verifySignature(payload: string, signature: string): boolean {
        const hmac = crypto.createHmac('sha256', this.secret);
        hmac.update(payload);
        const digest = hmac.digest('hex');
        return digest === signature;
    }
} 