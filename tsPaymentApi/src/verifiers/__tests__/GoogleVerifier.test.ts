import { GoogleVerifier } from '../googleVerifier';
import jwt from 'jsonwebtoken';

jest.mock('jsonwebtoken');

describe('GoogleVerifier', () => {
    let verifier: GoogleVerifier;
    const mockSecret = 'test-secret';

    beforeEach(() => {
        process.env.GOOGLE_PUBLIC_KEY = mockSecret;
        verifier = new GoogleVerifier();
    });

    afterEach(() => {
        jest.resetAllMocks();
        delete process.env.GOOGLE_PUBLIC_KEY;
    });

    describe('constructor', () => {
        it('should throw error if GOOGLE_PUBLIC_KEY is not set', () => {
            delete process.env.GOOGLE_PUBLIC_KEY;
            expect(() => new GoogleVerifier()).toThrow('GOOGLE_PUBLIC_KEY not set in environment variables.');
        });
    });

    describe('verifySignature', () => {
        const mockData = { test: 'data' };
        const mockSignature = 'valid-signature';

        it('should return true for valid signature', async () => {
            (jwt.verify as jest.Mock).mockReturnValue(true);
            const result = await verifier['verifySignature'](mockData, mockSignature);
            expect(result).toBe(true);
            expect(jwt.verify).toHaveBeenCalledWith(mockSignature, mockSecret, { algorithms: ['RS256'] });
        });

        it('should return false for invalid signature', async () => {
            (jwt.verify as jest.Mock).mockImplementation(() => {
                throw new jwt.JsonWebTokenError('invalid signature');
            });
            const result = await verifier['verifySignature'](mockData, mockSignature);
            expect(result).toBe(false);
        });

        it('should return false for expired token', async () => {
            (jwt.verify as jest.Mock).mockImplementation(() => {
                throw new jwt.TokenExpiredError('expired', new Date());
            });
            const result = await verifier['verifySignature'](mockData, mockSignature);
            expect(result).toBe(false);
        });

        it('should throw error for unexpected errors', async () => {
            (jwt.verify as jest.Mock).mockImplementation(() => {
                throw new Error('unexpected error');
            });
            await expect(verifier['verifySignature'](mockData, mockSignature)).rejects.toThrow('unexpected error');
        });
    });

    describe('getSignatureFromHeader', () => {
        it('should extract signature from headers', () => {
            const headers = { signature: 'valid-signature' };
            const result = verifier['getSignatureFromHeader'](headers);
            expect(result).toBe('valid-signature');
        });

        it('should throw error for missing signature', () => {
            const headers = {};
            expect(() => verifier['getSignatureFromHeader'](headers)).toThrow('Invalid or missing Google signature in headers');
        });

        it('should throw error for array signature', () => {
            const headers = { signature: ['sig1', 'sig2'] };
            expect(() => verifier['getSignatureFromHeader'](headers)).toThrow('Invalid or missing Google signature in headers');
        });
    });

    describe('verifyHeaderSignature', () => {
        const mockData = { test: 'data' };
        const mockHeaders = { signature: 'valid-signature' };

        it('should verify header signature successfully', async () => {
            (jwt.verify as jest.Mock).mockReturnValue(true);
            const result = await verifier.verifyHeaderSignature(mockData, mockHeaders);
            expect(result).toBe(true);
        });

        it('should throw error for invalid signature', async () => {
            (jwt.verify as jest.Mock).mockImplementation(() => {
                throw new jwt.JsonWebTokenError('invalid signature');
            });
            await expect(verifier.verifyHeaderSignature(mockData, mockHeaders)).rejects.toThrow('Bad signature');
        });
    });
}); 