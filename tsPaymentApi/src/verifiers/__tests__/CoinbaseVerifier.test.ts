import { CoinbaseVerifier } from '../coinbaseVerifier';
import crypto from 'crypto';

jest.mock('crypto');

describe('CoinbaseVerifier', () => {
    let verifier: CoinbaseVerifier;
    const mockSecret = 'test-secret';

    beforeEach(() => {
        process.env.COINBASE_SECRET = mockSecret;
        verifier = new CoinbaseVerifier();
    });

    afterEach(() => {
        jest.resetAllMocks();
        delete process.env.COINBASE_SECRET;
    });

    describe('constructor', () => {
        it('should throw error if COINBASE_SECRET is not set', () => {
            delete process.env.COINBASE_SECRET;
            expect(() => new CoinbaseVerifier()).toThrow('COINBASE_SECRET not set in environment variables.');
        });
    });

    describe('verifySignature', () => {
        const mockData = { test: 'data' };
        const mockSignature = 'valid-signature';
        const mockComputedSignature = 'computed-signature';

        beforeEach(() => {
            const mockHmac = {
                update: jest.fn().mockReturnThis(),
                digest: jest.fn().mockReturnValue(mockComputedSignature)
            };
            (crypto.createHmac as jest.Mock).mockReturnValue(mockHmac);
            (crypto.timingSafeEqual as jest.Mock).mockReturnValue(true);
        });

        it('should return true for valid signature', async () => {
            const result = await verifier['verifySignature'](mockData, mockSignature);
            expect(result).toBe(true);

            // Verify HMAC creation and usage
            expect(crypto.createHmac).toHaveBeenCalledWith('sha256', mockSecret);
            const mockHmac = (crypto.createHmac as jest.Mock).mock.results[0].value;
            expect(mockHmac.update).toHaveBeenCalledWith(JSON.stringify(mockData));
            expect(mockHmac.digest).toHaveBeenCalledWith('hex');

            // Verify timing-safe comparison
            expect(crypto.timingSafeEqual).toHaveBeenCalledWith(
                Buffer.from(mockComputedSignature),
                Buffer.from(mockSignature)
            );
        });

        it('should return false if signatures do not match', async () => {
            (crypto.timingSafeEqual as jest.Mock).mockReturnValue(false);
            const result = await verifier['verifySignature'](mockData, mockSignature);
            expect(result).toBe(false);
        });

        it('should return false if an error occurs during verification', async () => {
            (crypto.createHmac as jest.Mock).mockImplementation(() => {
                throw new Error('HMAC error');
            });
            const result = await verifier['verifySignature'](mockData, mockSignature);
            expect(result).toBe(false);
        });
    });

    describe('getSignatureFromHeader', () => {
        it('should extract signature from headers', () => {
            const headers = { 'cb-signature': 'valid-signature' };
            const result = verifier['getSignatureFromHeader'](headers);
            expect(result).toBe('valid-signature');
        });

        it('should throw error for missing signature', () => {
            const headers = {};
            expect(() => verifier['getSignatureFromHeader'](headers)).toThrow('Invalid or missing Coinbase signature in headers');
        });

        it('should throw error for array signature', () => {
            const headers = { 'cb-signature': ['sig1', 'sig2'] };
            expect(() => verifier['getSignatureFromHeader'](headers)).toThrow('Invalid or missing Coinbase signature in headers');
        });
    });

    describe('verifyHeaderSignature', () => {
        const mockData = { test: 'data' };
        const mockHeaders = { 'cb-signature': 'valid-signature' };
        const mockComputedSignature = 'computed-signature';

        beforeEach(() => {
            const mockHmac = {
                update: jest.fn().mockReturnThis(),
                digest: jest.fn().mockReturnValue(mockComputedSignature)
            };
            (crypto.createHmac as jest.Mock).mockReturnValue(mockHmac);
            (crypto.timingSafeEqual as jest.Mock).mockReturnValue(true);
        });

        it('should verify header signature successfully', async () => {
            const result = await verifier.verifyHeaderSignature(mockData, mockHeaders);
            expect(result).toBe(true);
        });

        it('should throw error for invalid signature', async () => {
            (crypto.timingSafeEqual as jest.Mock).mockReturnValue(false);
            await expect(verifier.verifyHeaderSignature(mockData, mockHeaders)).rejects.toThrow('Bad signature');
        });
    });
}); 