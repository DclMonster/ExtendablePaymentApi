import { WooCommerceVerifier } from '../woocommerceVerifier';
import crypto from 'crypto';
import axios from 'axios';
import { jest } from '@jest/globals';

jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

describe('WooCommerceVerifier', () => {
    let verifier: WooCommerceVerifier;

    beforeEach(() => {
        process.env.WOOCOMMERCE_WEBHOOK_SECRET = 'test_webhook_secret';
        process.env.WOOCOMMERCE_CONSUMER_KEY = 'test_consumer_key';
        process.env.WOOCOMMERCE_CONSUMER_SECRET = 'test_consumer_secret';
        process.env.WOOCOMMERCE_API_URL = 'https://test-store.com';
        
        verifier = new WooCommerceVerifier();
    });

    describe('initialization', () => {
        it('should initialize successfully with all env vars', () => {
            expect(verifier).toBeInstanceOf(WooCommerceVerifier);
        });

        it('should throw error when missing env vars', () => {
            delete process.env.WOOCOMMERCE_CONSUMER_KEY;
            expect(() => new WooCommerceVerifier()).toThrow('Missing required WooCommerce configuration');
        });
    });

    describe('verifySignature', () => {
        it('should verify valid signature', async () => {
            const payload = JSON.stringify({ id: '1234', total: '99.99' });
            const hmac = crypto.createHmac('sha256', 'test_webhook_secret');
            const signature = hmac.update(payload).digest('hex');

            const result = await verifier.verifySignature(payload, signature);
            expect(result).toBe(true);
        });

        it('should reject invalid signature', async () => {
            const payload = JSON.stringify({ id: '1234' });
            const result = await verifier.verifySignature(payload, 'invalid_signature');
            expect(result).toBe(false);
        });
    });

    describe('verifyOrder', () => {
        it('should verify order successfully', async () => {
            const orderData = { id: '1234', total: '99.99', status: 'completed' };
            mockedAxios.get.mockResolvedValueOnce({ data: orderData });

            const result = await verifier.verifyOrder('1234');
            expect(result.status).toBe('success');
            expect(result.order).toEqual(orderData);
        });

        it('should verify order with order key', async () => {
            const orderData = { id: '1234' };
            mockedAxios.get.mockResolvedValueOnce({ data: orderData });

            const result = await verifier.verifyOrder('1234', 'wc_order_abc123');
            expect(result.status).toBe('success');
            expect(mockedAxios.get).toHaveBeenCalledWith(
                expect.stringContaining('/orders/1234'),
                expect.objectContaining({
                    params: { order_key: 'wc_order_abc123' }
                })
            );
        });

        it('should handle verification failure', async () => {
            mockedAxios.get.mockRejectedValueOnce(new Error('Order not found'));

            const result = await verifier.verifyOrder('1234');
            expect(result.status).toBe('error');
            expect(result.error?.msg).toContain('Order not found');
        });
    });

    describe('verifySubscription', () => {
        it('should verify subscription successfully', async () => {
            const subscriptionData = { id: '5678', status: 'active' };
            mockedAxios.get.mockResolvedValueOnce({ data: subscriptionData });

            const result = await verifier.verifySubscription('5678');
            expect(result.status).toBe('success');
            expect(result.subscription).toEqual(subscriptionData);
        });

        it('should handle subscription verification failure', async () => {
            mockedAxios.get.mockRejectedValueOnce(new Error('Subscription not found'));

            const result = await verifier.verifySubscription('5678');
            expect(result.status).toBe('error');
            expect(result.error?.msg).toContain('Subscription not found');
        });
    });

    describe('handleNotification', () => {
        it.each([
            ['order.created', 'order_update'],
            ['order.updated', 'order_update'],
            ['subscription.created', 'subscription_update'],
            ['subscription.renewed', 'subscription_update'],
            ['subscription.cancelled', 'subscription_cancelled'],
            ['unknown.event', 'unknown_event']
        ])('should handle %s event', async (event, expectedType) => {
            const payload = {
                webhook_event: event,
                id: '1234',
                status: 'completed',
                line_items: [{ product_id: '789' }]
            };

            const result = await verifier.handleNotification(payload);
            expect(result.type).toBe(expectedType);

            if (expectedType !== 'unknown_event') {
                expect(result.status).toBe('action_update');
                expect(result.update_body).toBeDefined();
                expect(result.identifier).toBeDefined();
            }
        });

        it('should handle notification error', async () => {
            const result = await verifier.handleNotification(null as any);
            expect(result.status).toBe('error');
            expect(result.type).toBe('processing_error');
            expect(result.update_body.error).toBeDefined();
        });
    });
}); 