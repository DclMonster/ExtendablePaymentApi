import { SignatureVerifier } from '../SignatureVerifier';
import { IncomingHttpHeaders } from 'http';

// Mock implementation for testing
class TestVerifier extends SignatureVerifier {
    constructor() {
        super('TEST_SECRET');
    }

    protected async verifySignature(data: Record<string, any>, signature: string): Promise<boolean> {
        // Simple mock implementation that validates if signature matches 'valid-signature'
        return signature === 'valid-signature';
    }

    protected getSignatureFromHeader(headers: IncomingHttpHeaders): string {
        const signature = headers['test-signature'];
        if (!signature || Array.isArray(signature)) {
            throw new Error('Invalid or missing test signature in headers');
        }
        return signature;
    }
}

describe('SignatureVerifier', () => {
    let verifier: TestVerifier;
    const mockSecret = 'test-secret';

    beforeEach(() => {
        process.env.TEST_SECRET = mockSecret;
        verifier = new TestVerifier();
    });

    afterEach(() => {
        delete process.env.TEST_SECRET;
    });

    describe('constructor', () => {
        it('should initialize with secret from environment', () => {
            expect(verifier['secret']).toBe(mockSecret);
        });

        it('should throw error if secret is not set in environment', () => {
            delete process.env.TEST_SECRET;
            expect(() => new TestVerifier()).toThrow('TEST_SECRET not set in environment variables.');
        });
    });

    describe('verifyHeaderSignature', () => {
        const mockData = { test: 'data' };

        it('should return true for valid signature', async () => {
            const headers = { 'test-signature': 'valid-signature' };
            const result = await verifier.verifyHeaderSignature(mockData, headers);
            expect(result).toBe(true);
        });

        it('should throw error for invalid signature', async () => {
            const headers = { 'test-signature': 'invalid-signature' };
            await expect(verifier.verifyHeaderSignature(mockData, headers))
                .rejects
                .toThrow('Bad signature');
        });

        it('should throw error for missing signature header', async () => {
            const headers = {};
            await expect(verifier.verifyHeaderSignature(mockData, headers))
                .rejects
                .toThrow('Invalid or missing test signature in headers');
        });

        it('should throw error for array signature header', async () => {
            const headers = { 'test-signature': ['sig1', 'sig2'] };
            await expect(verifier.verifyHeaderSignature(mockData, headers))
                .rejects
                .toThrow('Invalid or missing test signature in headers');
        });

        it('should handle errors from verifySignature', async () => {
            const headers = { 'test-signature': 'error-signature' };
            const errorVerifier = new class extends TestVerifier {
                protected async verifySignature(): Promise<boolean> {
                    throw new Error('Verification error');
                }
            }();
            process.env.TEST_SECRET = mockSecret;

            await expect(errorVerifier.verifyHeaderSignature(mockData, headers))
                .rejects
                .toThrow('Verification error');
        });
    });

    describe('getSecretFromEnv', () => {
        it('should return secret from environment', () => {
            const secret = verifier['getSecretFromEnv']('TEST_SECRET');
            expect(secret).toBe(mockSecret);
        });

        it('should throw error if secret is not set', () => {
            delete process.env.TEST_SECRET;
            expect(() => verifier['getSecretFromEnv']('TEST_SECRET'))
                .toThrow('TEST_SECRET not set in environment variables.');
        });

        it('should throw error if secret is empty string', () => {
            process.env.TEST_SECRET = '';
            expect(() => verifier['getSecretFromEnv']('TEST_SECRET'))
                .toThrow('TEST_SECRET not set in environment variables.');
        });
    });
}); 