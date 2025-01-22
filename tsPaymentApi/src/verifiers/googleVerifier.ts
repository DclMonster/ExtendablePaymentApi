import { IncomingHttpHeaders } from 'http';
import { SignatureVerifier } from './abstract/SignatureVerifier';
import jwt from 'jsonwebtoken';

export class GoogleVerifier extends SignatureVerifier {
    constructor() {
        super('GOOGLE_PUBLIC_KEY');
    }

    protected async verifySignature(data: Record<string, any>, signature: string): Promise<boolean> {
        try {
            jwt.verify(signature, this.secret, { algorithms: ['RS256'] });
            return true;
        } catch (error) {
            if (error instanceof jwt.JsonWebTokenError || error instanceof jwt.TokenExpiredError) {
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
} 