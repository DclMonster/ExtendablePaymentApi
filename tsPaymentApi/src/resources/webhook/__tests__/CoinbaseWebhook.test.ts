import { CoinbaseWebhook, CoinbaseWebhookError } from '../CoinbaseWebhook';
import { Forwarder } from '../../../services/forwarder/abstract/Forwarder';

describe('CoinbaseWebhook', () => {
    let webhook: CoinbaseWebhook;
    let mockForwarder: Forwarder;

    beforeEach(() => {
        mockForwarder = {
            forwardEvent: jest.fn().mockResolvedValue(undefined)
        };
        webhook = new CoinbaseWebhook(mockForwarder);
    });

    describe('parseEventData', () => {
        it('should parse valid Coinbase event data', () => {
            const eventData = JSON.stringify({
                event: {
                    type: 'charge:confirmed',
                    data: {
                        code: 'test_transaction',
                        status: 'completed',
                        pricing: {
                            local: {
                                amount: '9.99',
                                currency: 'USD'
                            }
                        },
                        metadata: {
                            user_id: 'test_user',
                            subscription_id: 'test_subscription'
                        }
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
                subscriptionId: 'test_subscription'
            });
        });

        it('should throw error for missing required fields', () => {
            const eventData = JSON.stringify({
                event: {
                    type: 'charge:confirmed',
                    data: {}
                }
            });

            expect(() => webhook['parseEventData'](eventData))
                .toThrow(CoinbaseWebhookError);
        });

        it('should throw error for invalid JSON', () => {
            const eventData = 'invalid json';

            expect(() => webhook['parseEventData'](eventData))
                .toThrow(CoinbaseWebhookError);
        });
    });

    describe('mapStatus', () => {
        it('should map charge:confirmed with completed status to paid', () => {
            expect(webhook['mapStatus']('charge:confirmed', 'completed')).toBe('paid');
        });

        it('should map charge:resolved to paid', () => {
            expect(webhook['mapStatus']('charge:resolved', '')).toBe('paid');
        });

        it('should map charge:pending to sent_to_websocket', () => {
            expect(webhook['mapStatus']('charge:pending', '')).toBe('sent_to_websocket');
        });

        it('should map charge:delayed to sent_to_processor', () => {
            expect(webhook['mapStatus']('charge:delayed', '')).toBe('sent_to_processor');
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
                userId: 'test_user'
            };

            const result = webhook['getOneTimePaymentData'](eventData);

            expect(result).toEqual({
                userId: 'test_user',
                itemCategory: 'ONE_TIME',
                purchaseId: 'test_transaction',
                itemName: 'Coinbase Payment',
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
                userId: 'test_user'
            };

            const result = webhook['getSubscriptionPaymentData'](eventData);

            expect(result).toEqual({
                userId: 'test_user',
                itemCategory: 'SUBSCRIPTION',
                purchaseId: 'test_transaction',
                itemName: 'Coinbase Payment',
                status: 'paid',
                timeBought: expect.any(String)
            });
        });
    });
}); 