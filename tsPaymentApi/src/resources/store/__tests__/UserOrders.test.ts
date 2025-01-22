import { UserOrders } from '../UserOrders';
import { Request, Response } from 'express';
import { getServices } from '../../../services';
import { jest, describe, it, beforeEach, expect } from '@jest/globals';

jest.mock('../../../services', () => ({
    getServices: jest.fn()
}));

describe('UserOrders', () => {
    let userOrders: UserOrders;
    let mockRequest: Partial<Request>;
    let mockResponse: Partial<Response>;
    let mockServices: any;

    beforeEach(() => {
        jest.clearAllMocks();

        mockServices = {
            getOrdersByUserId: jest.fn()
        };
        (getServices as jest.Mock).mockReturnValue(mockServices);

        mockRequest = {
            query: {}
        };
        mockResponse = {
            status: jest.fn().mockReturnThis(),
            json: jest.fn().mockReturnThis()
        } as Partial<Response>;

        userOrders = new UserOrders();
    });

    describe('get', () => {
        it('should return orders successfully', async () => {
            const userId = 'test-user-id';
            const mockOrders = [
                { id: '1', status: 'completed' },
                { id: '2', status: 'pending' }
            ];
            mockRequest.query = { user_id: userId };
            mockServices.getOrdersByUserId.mockResolvedValue(mockOrders);

            await userOrders['get'](
                mockRequest as Request,
                mockResponse as Response
            );

            expect(mockServices.getOrdersByUserId).toHaveBeenCalledWith(userId);
            expect(mockResponse.status).toHaveBeenCalledWith(200);
            expect(mockResponse.json).toHaveBeenCalledWith({ orders: mockOrders });
        });

        it('should return 400 when user_id is missing', async () => {
            await userOrders['get'](
                mockRequest as Request,
                mockResponse as Response
            );

            expect(mockServices.getOrdersByUserId).not.toHaveBeenCalled();
            expect(mockResponse.status).toHaveBeenCalledWith(400);
            expect(mockResponse.json).toHaveBeenCalledWith({ error: 'User ID is required' });
        });

        it('should handle errors appropriately', async () => {
            const userId = 'test-user-id';
            const error = new Error('Failed to fetch orders');
            mockRequest.query = { user_id: userId };
            mockServices.getOrdersByUserId.mockRejectedValue(error);

            await userOrders['get'](
                mockRequest as Request,
                mockResponse as Response
            );

            expect(mockServices.getOrdersByUserId).toHaveBeenCalledWith(userId);
            expect(mockResponse.status).toHaveBeenCalledWith(500);
            expect(mockResponse.json).toHaveBeenCalledWith({
                error: 'Failed to retrieve user orders',
                details: error.message
            });
        });

        it('should handle non-Error objects in catch block', async () => {
            const userId = 'test-user-id';
            const errorString = 'Unknown error';
            mockRequest.query = { user_id: userId };
            mockServices.getOrdersByUserId.mockRejectedValue(errorString);

            await userOrders['get'](
                mockRequest as Request,
                mockResponse as Response
            );

            expect(mockServices.getOrdersByUserId).toHaveBeenCalledWith(userId);
            expect(mockResponse.status).toHaveBeenCalledWith(500);
            expect(mockResponse.json).toHaveBeenCalledWith({
                error: 'Failed to retrieve user orders',
                details: errorString
            });
        });
    });
}); 