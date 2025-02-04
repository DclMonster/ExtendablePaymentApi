import { PayPalVerifier } from '../PaypalVerifier';
import axios from 'axios';
import * as crypto from 'crypto';

jest.mock('axios');
jest.mock('crypto');

describe('PayPalVerifier', () => {
    let verifier: PayPalVerifier;
    const mockSecret = 'test-secret';
    const mockWebhookId = 'test-webhook-id';

    beforeEach(() => {
        process.env.PAYPAL_SECRET = mockSecret;
        process.env.PAYPAL_WEBHOOK_ID = mockWebhookId;
        verifier = new PayPalVerifier();
    });

    afterEach(() => {
        jest.resetAllMocks();
        delete process.env.PAYPAL_SECRET;
        delete process.env.PAYPAL_WEBHOOK_ID;
    });

    describe('constructor', () => {
        it('should throw error if PAYPAL_SECRET is not set', () => {
            delete process.env.PAYPAL_SECRET;
            expect(() => new PayPalVerifier()).toThrow('PAYPAL_SECRET not set in environment variables.');
        });

        it('should throw error if PAYPAL_WEBHOOK_ID is not set', () => {
            delete process.env.PAYPAL_WEBHOOK_ID;
            expect(() => new PayPalVerifier()).toThrow('PAYPAL_WEBHOOK_ID not set in environment variables.');
        });
    });

    describe('verifySignature', () => {
        const mockData = {
            transmissionId: 'trans-123',
            timestamp: '2024-01-22T00:00:00Z',
            webhookId: mockWebhookId,
            eventBody: '{"test": "data"}',
            certUrl: 'https://api.paypal.com/cert',
            authAlgo: 'SHA256withRSA'
        };
        const mockSignature = 'valid-signature';
        const mockCertData = '-----BEGIN CERTIFICATE-----\nMOCK_CERT\n-----END CERTIFICATE-----';

        beforeEach(() => {
            (axios.get as jest.Mock).mockResolvedValue({ data: mockCertData });
            const mockVerify = {
                update: jest.fn().mockReturnThis(),
                verify: jest.fn().mockReturnValue(true)
            };
            (crypto.createVerify as jest.Mock).mockReturnValue(mockVerify);
        });

        it('should return true for valid signature', async () => {
            const result = await verifier['verifySignature'](mockData, mockSignature);
            expect(result).toBe(true);

            // Verify the message construction
            const expectedMessage = `${mockData.transmissionId}|${mockData.timestamp}|${mockData.webhookId}|${mockData.eventBody}`;
            expect(crypto.createVerify).toHaveBeenCalledWith('SHA256');
            const mockVerify = (crypto.createVerify as jest.Mock).mock.results[0].value;
            expect(mockVerify.update).toHaveBeenCalledWith(expectedMessage);
        });

        it('should return false if webhook ID does not match', async () => {
            const invalidData = { ...mockData, webhookId: 'wrong-id' };
            const result = await verifier['verifySignature'](invalidData, mockSignature);
            expect(result).toBe(false);
        });

        it('should return false if auth algo is not supported', async () => {
            const invalidData = { ...mockData, authAlgo: 'UNSUPPORTED' };
            const result = await verifier['verifySignature'](invalidData, mockSignature);
            expect(result).toBe(false);
        });

        it('should return false if certificate fetch fails', async () => {
            (axios.get as jest.Mock).mockRejectedValue(new Error('Network error'));
            const result = await verifier['verifySignature'](mockData, mockSignature);
            expect(result).toBe(false);
        });

        it('should return false if signature verification fails', async () => {
            const mockVerify = {
                update: jest.fn().mockReturnThis(),
                verify: jest.fn().mockReturnValue(false)
            };
            (crypto.createVerify as jest.Mock).mockReturnValue(mockVerify);
            const result = await verifier['verifySignature'](mockData, mockSignature);
            expect(result).toBe(false);
        });
    });

    describe('getSignatureFromHeader', () => {
        it('should extract signature from headers', () => {
            const headers = { 'paypal-auth-algo': 'valid-signature' };
            const result = verifier['getSignatureFromHeader'](headers);
            expect(result).toBe('valid-signature');
        });

        it('should throw error for missing signature', () => {
            const headers = {};
            expect(() => verifier['getSignatureFromHeader'](headers)).toThrow('Invalid or missing PayPal signature in headers');
        });

        it('should throw error for array signature', () => {
            const headers = { 'paypal-auth-algo': ['sig1', 'sig2'] };
            expect(() => verifier['getSignatureFromHeader'](headers)).toThrow('Invalid or missing PayPal signature in headers');
        });
    });

    describe('verifyHeaderSignature', () => {
        const mockData = {
            transmissionId: 'trans-123',
            timestamp: '2024-01-22T00:00:00Z',
            webhookId: mockWebhookId,
            eventBody: '{"test": "data"}',
            certUrl: 'https://api.paypal.com/cert',
            authAlgo: 'SHA256withRSA'
        };
        const mockHeaders = { 'paypal-auth-algo': 'valid-signature' };

        beforeEach(() => {
            const mockVerify = {
                update: jest.fn().mockReturnThis(),
                verify: jest.fn().mockReturnValue(true)
            };
            (crypto.createVerify as jest.Mock).mockReturnValue(mockVerify);
            (axios.get as jest.Mock).mockResolvedValue({ data: '-----BEGIN CERTIFICATE-----\nMOCK_CERT\n-----END CERTIFICATE-----' });
        });

        it('should verify header signature successfully', async () => {
            const result = await verifier.verifyHeaderSignature(mockData, mockHeaders);
            expect(result).toBe(true);
        });

        it('should throw error for invalid signature', async () => {
            const mockVerify = {
                update: jest.fn().mockReturnThis(),
                verify: jest.fn().mockReturnValue(false)
            };
            (crypto.createVerify as jest.Mock).mockReturnValue(mockVerify);
            await expect(verifier.verifyHeaderSignature(mockData, mockHeaders)).rejects.toThrow('Bad signature');
        });
    });
}); 