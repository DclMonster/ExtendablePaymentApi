import { IncomingHttpHeaders } from 'http';
import { SignatureVerifier } from './abstract/SignatureVerifier';
import jwt from 'jsonwebtoken';

interface AppleWebhookData {
    transactionId: string;
    [key: string]: any;
}

export class AppleVerifier extends SignatureVerifier {
    constructor() {
        super('APPLE_PUBLIC_KEY');
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
} 