import { WooCommerceWebhook } from '../woocommerce';
import { woocommerceVerifier } from '../../../verifiers/woocommerceVerifier';
import { PaymentProvider } from '../../../services/enums';
import { jest } from '@jest/globals';
import { Request, Response } from 'express';

jest.mock('../../../verifiers/woocommerceVerifier');
const mockedVerifier = woocommerceVerifier as jest.Mocked<typeof woocommerceVerifier>;

describe('WooCommerceWebhook', () => {
    let webhook: WooCommerceWebhook;
    let mockReq: Partial<Request>;
    let mockRes: Partial<Response>;
    let mockForwarder: jest.Mock;

    beforeEach(() => {
        mockForwarder = jest.fn();
        webhook = new WooCommerceWebhook(mockForwarder);

        mockRes = {
            status: jest.fn().mockReturnThis(),
            json: jest.fn()
        };

        mockReq = {
            body: {
                id: '1234',
                status: 'completed',
                total: '99.99',
                currency: 'USD',
                customer_id: 'user123',
                line_items: [{
                    product_id: '789',
                    name: 'Test Product'
                }]
            },
            headers: {
                'x-wc-webhook-signature': 'valid_signature'
            }
        };

        // Reset all mocks
        jest.clearAllMocks();
    });

    describe('post', () => {
        it('should process one-time payment successfully', async () => {
            mockedVerifier.verifySignature.mockResolvedValue(true);
            mockedVerifier.verifyOrder.mockResolvedValue({
                status: 'success',
                order: mockReq.body
            });

            await webhook.post(mockReq as Request, mockRes as Response);

            expect(mockForwarder).toHaveBeenCalledWith({
                provider: PaymentProvider.WOOCOMMERCE,
                user_id: 'user123',
                transaction_id: '1234',
                amount: '99.99',
                currency: 'USD',
                status: 'paid',
                metadata: expect.any(Object)
            });

            expect(mockRes.status).toHaveBeenCalledWith(200);
            expect(mockRes.json).toHaveBeenCalledWith({ status: 'success' });
        });

        it('should process subscription payment successfully', async () => {
            mockReq.body.webhook_event = 'subscription.created';
            mockedVerifier.verifySignature.mockResolvedValue(true);
            mockedVerifier.verifySubscription.mockResolvedValue({
                status: 'success',
                subscription: mockReq.body
            });

            await webhook.post(mockReq as Request, mockRes as Response);

            expect(mockForwarder).toHaveBeenCalledWith({
                provider: PaymentProvider.WOOCOMMERCE,
                user_id: 'user123',
                transaction_id: '1234',
                amount: '99.99',
                currency: 'USD',
                status: 'active',
                is_subscription: true,
                metadata: expect.any(Object)
            });

            expect(mockRes.status).toHaveBeenCalledWith(200);
            expect(mockRes.json).toHaveBeenCalledWith({ status: 'success' });
        });

        it('should handle invalid signature', async () => {
            mockedVerifier.verifySignature.mockResolvedValue(false);

            await webhook.post(mockReq as Request, mockRes as Response);

            expect(mockRes.status).toHaveBeenCalledWith(400);
            expect(mockRes.json).toHaveBeenCalledWith({
                status: 'error',
                message: 'Invalid signature'
            });
            expect(mockForwarder).not.toHaveBeenCalled();
        });

        it('should handle missing signature header', async () => {
            delete mockReq.headers['x-wc-webhook-signature'];

            await webhook.post(mockReq as Request, mockRes as Response);

            expect(mockRes.status).toHaveBeenCalledWith(400);
            expect(mockRes.json).toHaveBeenCalledWith({
                status: 'error',
                message: 'Missing signature header'
            });
            expect(mockForwarder).not.toHaveBeenCalled();
        });

        it('should handle order verification failure', async () => {
            mockedVerifier.verifySignature.mockResolvedValue(true);
            mockedVerifier.verifyOrder.mockResolvedValue({
                status: 'error',
                error: { msg: 'Order not found' }
            });

            await webhook.post(mockReq as Request, mockRes as Response);

            expect(mockRes.status).toHaveBeenCalledWith(400);
            expect(mockRes.json).toHaveBeenCalledWith({
                status: 'error',
                message: 'Order verification failed: Order not found'
            });
            expect(mockForwarder).not.toHaveBeenCalled();
        });

        it('should handle subscription verification failure', async () => {
            mockReq.body.webhook_event = 'subscription.created';
            mockedVerifier.verifySignature.mockResolvedValue(true);
            mockedVerifier.verifySubscription.mockResolvedValue({
                status: 'error',
                error: { msg: 'Subscription not found' }
            });

            await webhook.post(mockReq as Request, mockRes as Response);

            expect(mockRes.status).toHaveBeenCalledWith(400);
            expect(mockRes.json).toHaveBeenCalledWith({
                status: 'error',
                message: 'Subscription verification failed: Subscription not found'
            });
            expect(mockForwarder).not.toHaveBeenCalled();
        });

        it('should handle unexpected errors', async () => {
            mockedVerifier.verifySignature.mockRejectedValue(new Error('Unexpected error'));

            await webhook.post(mockReq as Request, mockRes as Response);

            expect(mockRes.status).toHaveBeenCalledWith(500);
            expect(mockRes.json).toHaveBeenCalledWith({
                status: 'error',
                message: 'Internal server error: Unexpected error'
            });
            expect(mockForwarder).not.toHaveBeenCalled();
        });
    });
}); 