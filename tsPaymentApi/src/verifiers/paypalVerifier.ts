import { IncomingHttpHeaders } from 'http';
import { SignatureVerifier } from './abstract/SignatureVerifier';
import axios from 'axios';
import * as crypto from 'crypto';

interface PayPalWebhookData {
    transmissionId: string;
    timestamp: string;
    webhookId: string;
    eventBody: string;
    certUrl: string;
    authAlgo: string;
}

export class PayPalVerifier extends SignatureVerifier {
    private webhookId: string;

    constructor() {
        super('PAYPAL_SECRET');
        const webhookId = process.env.PAYPAL_WEBHOOK_ID;
        if (!webhookId) {
            throw new Error('PAYPAL_WEBHOOK_ID not set in environment variables.');
        }
        this.webhookId = webhookId;
    }

    protected async verifySignature(data: PayPalWebhookData, signature: string): Promise<boolean> {
        try {
            const {
                transmissionId,
                timestamp,
                webhookId,
                eventBody,
                certUrl,
                authAlgo
            } = data;

            // Ensure the webhook_id matches the expected one
            if (webhookId !== this.webhookId) {
                throw new Error('Webhook ID does not match the expected value.');
            }

            // Step 1: Fetch PayPal's public certificate
            const response = await axios.get(certUrl);
            const certData = response.data;

            // Step 2: Construct the expected message
            const expectedMessage = `${transmissionId}|${timestamp}|${webhookId}|${eventBody}`;

            // Step 3: Decode the actual signature from base64
            const decodedSignature = Buffer.from(signature, 'base64');

            // Step 4: Determine the hash algorithm
            if (authAlgo !== 'SHA256withRSA') {
                throw new Error(`Unsupported auth_algo: ${authAlgo}`);
            }

            // Step 5: Verify the signature
            const verify = crypto.createVerify('SHA256');
            verify.update(expectedMessage);
            const isValid = verify.verify(certData, decodedSignature);

            return isValid;
        } catch (error) {
            console.error('Signature verification failed:', error);
            return false;
        }
    }

    protected getSignatureFromHeader(headers: IncomingHttpHeaders): string {
        const signature = headers['paypal-auth-algo'];
        if (!signature || Array.isArray(signature)) {
            throw new Error('Invalid or missing PayPal signature in headers');
        }
        return signature;
    }
} 