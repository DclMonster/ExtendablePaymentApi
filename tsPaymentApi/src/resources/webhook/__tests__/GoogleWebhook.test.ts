import { GoogleWebhook, GoogleWebhookError } from '../GoogleWebhook';
import { Forwarder } from '../../../services/forwarder/abstract/Forwarder';

describe('GoogleWebhook', () => {
    let webhook: GoogleWebhook;
    let mockForwarder: Forwarder;

    beforeEach(() => {
        mockForwarder = {
            forwardEvent: jest.fn().mockResolvedValue(undefined)
        };
        webhook = new GoogleWebhook(mockForwarder);
    });

    describe('parseEventData', () => {
        it('should parse valid Google event data', () => {
            const eventData = JSON.stringify({
                message: {
                    data: {
                        subscriptionNotification: {
                            orderId: 'test_transaction',
                            priceAmountMicros: '9990000',
                            priceCurrencyCode: 'USD',
                            notificationType: 'SUBSCRIPTION_PURCHASED'
                        },
                        userId: 'test_user'
                    }
                }
            });

            const result = webhook['parseEventData'](eventData);

            expect(result).toEqual({
                transactionId: 'test_transaction',
                amount: 9.99,
                currency: 'USD',
                status: 'paid',
                userId: 'test_user',
                subscriptionId: undefined
            });
        });

        it('should throw error for missing required fields', () => {
            const eventData = JSON.stringify({
                message: {
                    data: {
                        subscriptionNotification: {}
                    }
                }
            });

            expect(() => webhook['parseEventData'](eventData))
                .toThrow(GoogleWebhookError);
        });

        it('should throw error for invalid JSON', () => {
            const eventData = 'invalid json';

            expect(() => webhook['parseEventData'](eventData))
                .toThrow(GoogleWebhookError);
        });
    });

    describe('mapStatus', () => {
        it('should map SUBSCRIPTION_PURCHASED to paid', () => {
            expect(webhook['mapStatus']('SUBSCRIPTION_PURCHASED')).toBe('paid');
        });

        it('should map SUBSCRIPTION_RENEWED to paid', () => {
            expect(webhook['mapStatus']('SUBSCRIPTION_RENEWED')).toBe('paid');
        });

        it('should map SUBSCRIPTION_CANCELED to sent_to_processor', () => {
            expect(webhook['mapStatus']('SUBSCRIPTION_CANCELED')).toBe('sent_to_processor');
        });

        it('should map unknown status to webhook_received', () => {
            expect(webhook['mapStatus']('UNKNOWN')).toBe('webhook_received');
        });
    });

    describe('getOneTimePaymentData', () => {
        it('should create one-time payment data', () => {
            const eventData = {
                transactionId: 'test_transaction',
                amount: 9.99,
                currency: 'USD',
                status: 'paid' as const,
                userId: 'test_user',
                subscriptionId: 'test_subscription'
            };

            const result = webhook['getOneTimePaymentData'](eventData);

            expect(result).toEqual({
                userId: 'test_user',
                itemCategory: 'ONE_TIME',
                purchaseId: 'test_transaction',
                itemName: 'test_subscription',
                status: 'paid',
                quantity: 1,
                timeBought: expect.any(String)
            });
        });
    });

    describe('getSubscriptionPaymentData', () => {
        it('should create subscription payment data', () => {
            const eventData = {
                transactionId: 'test_transaction',
                amount: 9.99,
                currency: 'USD',
                status: 'paid' as const,
                userId: 'test_user',
                subscriptionId: 'test_subscription'
            };

            const result = webhook['getSubscriptionPaymentData'](eventData);

            expect(result).toEqual({
                userId: 'test_user',
                itemCategory: 'SUBSCRIPTION',
                purchaseId: 'test_transaction',
                itemName: 'test_subscription',
                status: 'paid',
                timeBought: expect.any(String)
            });
        });
    });
}); 