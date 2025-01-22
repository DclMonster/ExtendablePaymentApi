import { AppleWebhook, AppleWebhookError } from '../AppleWebhook';
import { Forwarder } from '../../../services/forwarder/abstract/Forwarder';

describe('AppleWebhook', () => {
    let webhook: AppleWebhook;
    let mockForwarder: Forwarder;

    beforeEach(() => {
        mockForwarder = {
            forwardEvent: jest.fn().mockResolvedValue(undefined)
        };
        webhook = new AppleWebhook(mockForwarder);
    });

    describe('parseEventData', () => {
        it('should parse valid Apple event data', () => {
            const eventData = JSON.stringify({
                notificationType: 'INITIAL_BUY',
                unifiedReceipt: {
                    latestReceiptInfo: [{
                        transactionId: 'test_transaction',
                        price: '9.99',
                        currency: 'USD'
                    }]
                },
                userId: 'test_user'
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
                notificationType: 'INITIAL_BUY',
                unifiedReceipt: {
                    latestReceiptInfo: [{}]
                }
            });

            expect(() => webhook['parseEventData'](eventData))
                .toThrow(AppleWebhookError);
        });

        it('should throw error for invalid JSON', () => {
            const eventData = 'invalid json';

            expect(() => webhook['parseEventData'](eventData))
                .toThrow(AppleWebhookError);
        });
    });

    describe('mapStatus', () => {
        it('should map INITIAL_BUY to paid', () => {
            expect(webhook['mapStatus']('INITIAL_BUY')).toBe('paid');
        });

        it('should map DID_RENEW to paid', () => {
            expect(webhook['mapStatus']('DID_RENEW')).toBe('paid');
        });

        it('should map CANCEL to sent_to_processor', () => {
            expect(webhook['mapStatus']('CANCEL')).toBe('sent_to_processor');
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
                userId: 'test_user'
            };

            const result = webhook['getOneTimePaymentData'](eventData);

            expect(result).toEqual({
                userId: 'test_user',
                itemCategory: 'ONE_TIME',
                purchaseId: 'test_transaction',
                itemName: 'Apple Payment',
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
                itemName: 'Apple Payment',
                status: 'paid',
                timeBought: expect.any(String)
            });
        });
    });
}); 