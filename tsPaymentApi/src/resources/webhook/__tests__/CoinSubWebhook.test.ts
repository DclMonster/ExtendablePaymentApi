import { CoinSubWebhook, CoinSubWebhookError } from '../CoinSubWebhook';
import { Forwarder } from '../../../services/forwarder/abstract/Forwarder';

describe('CoinSubWebhook', () => {
    let webhook: CoinSubWebhook;
    let mockForwarder: Forwarder;

    beforeEach(() => {
        mockForwarder = {
            forwardEvent: jest.fn().mockResolvedValue(undefined)
        };
        webhook = new CoinSubWebhook(mockForwarder);
    });

    describe('parseEventData', () => {
        it('should parse valid CoinSub event data', () => {
            const eventData = JSON.stringify({
                event_type: 'subscription_activated',
                subscription: {
                    transaction_id: 'test_transaction',
                    amount: '9.99',
                    currency: 'USD',
                    status: 'active',
                    user_id: 'test_user',
                    subscription_id: 'test_subscription'
                }
            });

            const result = webhook['parseEventData'](eventData);

            expect(result).toEqual({
                transactionId: 'test_transaction',
                amount: 9.99,
                currency: 'USD',
                status: 'paid',
                userId: 'test_user',
                subscriptionId: 'test_subscription'
            });
        });

        it('should throw error for missing required fields', () => {
            const eventData = JSON.stringify({
                event_type: 'subscription_activated',
                subscription: {}
            });

            expect(() => webhook['parseEventData'](eventData))
                .toThrow(CoinSubWebhookError);
        });

        it('should throw error for invalid JSON', () => {
            const eventData = 'invalid json';

            expect(() => webhook['parseEventData'](eventData))
                .toThrow(CoinSubWebhookError);
        });
    });

    describe('mapStatus', () => {
        it('should map subscription_activated to paid', () => {
            expect(webhook['mapStatus']('subscription_activated', '')).toBe('paid');
        });

        it('should map subscription_renewed to paid', () => {
            expect(webhook['mapStatus']('subscription_renewed', '')).toBe('paid');
        });

        it('should map subscription_canceled to sent_to_processor', () => {
            expect(webhook['mapStatus']('subscription_canceled', '')).toBe('sent_to_processor');
        });

        it('should map subscription_expired to sent_to_processor', () => {
            expect(webhook['mapStatus']('subscription_expired', '')).toBe('sent_to_processor');
        });

        it('should map unknown status to webhook_received', () => {
            expect(webhook['mapStatus']('unknown', '')).toBe('webhook_received');
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