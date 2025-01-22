import { StoreItems } from '../StoreItems';
import { Request, Response } from 'express';
import { getServices } from '../../../services';
import { jest, describe, it, beforeEach, expect } from '@jest/globals';
// Mock the services module
jest.mock('../../../services', () => ({
    getServices: jest.fn()
}));

describe('StoreItems', () => {
    let storeItems: StoreItems;
    let mockRequest: Partial<Request>;
    let mockResponse: Partial<Response>;
    let mockServices: any;

    beforeEach(() => {
        // Reset mocks
        jest.clearAllMocks();

        // Create mock services
        mockServices = {
            getAllItems: jest.fn()
        };
        (getServices as jest.Mock).mockReturnValue(mockServices);

        // Create mock request and response
        mockRequest = {};
        mockResponse = {
            status: jest.fn().mockReturnThis(),
            json: jest.fn()
        };

        // Create instance of StoreItems
        storeItems = new StoreItems();
    });

    describe('get', () => {
        it('should return items successfully', async () => {
            const mockItems = [
                { id: '1', name: 'Item 1', price: 10 },
                { id: '2', name: 'Item 2', price: 20 }
            ];
            mockServices.getAllItems.mockResolvedValue(mockItems);

            await storeItems['get'](
                mockRequest as Request,
                mockResponse as Response
            );

            expect(mockServices.getAllItems).toHaveBeenCalled();
            expect(mockResponse.status).toHaveBeenCalledWith(200);
            expect(mockResponse.json).toHaveBeenCalledWith({ items: mockItems });
        });

        it('should handle errors appropriately', async () => {
            const error = new Error('Failed to fetch items');
            mockServices.getAllItems.mockRejectedValue(error);

            await storeItems['get'](
                mockRequest as Request,
                mockResponse as Response
            );

            expect(mockServices.getAllItems).toHaveBeenCalled();
            expect(mockResponse.status).toHaveBeenCalledWith(500);
            expect(mockResponse.json).toHaveBeenCalledWith({
                error: 'Failed to retrieve store items',
                details: error.message
            });
        });

        it('should handle non-Error objects in catch block', async () => {
            const errorString = 'Unknown error';
            mockServices.getAllItems.mockRejectedValue(errorString);

            await storeItems['get'](
                mockRequest as Request,
                mockResponse as Response
            );

            expect(mockServices.getAllItems).toHaveBeenCalled();
            expect(mockResponse.status).toHaveBeenCalledWith(500);
            expect(mockResponse.json).toHaveBeenCalledWith({
                error: 'Failed to retrieve store items',
                details: errorString
            });
        });
    });
}); 