import { IncomingHttpHeaders } from 'http';
import dotenv from 'dotenv';

export abstract class SignatureVerifier {
    protected secret: string;

    constructor(secretKey: string) {
        this.secret = this.getSecretFromEnv(secretKey);
    }

    public async verifyHeaderSignature(data: Record<string, any>, headers: IncomingHttpHeaders): Promise<boolean> {
        const signature = this.getSignatureFromHeader(headers);
        if (!await this.verifySignature(data, signature)) {
            throw new Error('Bad signature');
        }
        return true;
    }

    protected abstract verifySignature(data: Record<string, any>, signature: string): Promise<boolean>;

    protected abstract getSignatureFromHeader(headers: IncomingHttpHeaders): string;

    private getSecretFromEnv(key: string): string {
        const secret = process.env[key];
        if (!secret) {
            throw new Error(`${key} not set in environment variables.`);
        }
        return secret;
    }
} 