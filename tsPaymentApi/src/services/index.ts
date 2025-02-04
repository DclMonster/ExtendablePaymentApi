import { SubscriptionService } from './subscriptionService';
import { PaymentService } from './paymentService';
import { Services } from './Services';

const subscriptionService = new SubscriptionService();
const paymentService = new PaymentService();

let servicesInstance: Services | null = null;

export const getServices = (): Services => {
    if (!servicesInstance) {
        throw new Error('Services not initialized');
    }
    return servicesInstance;
};

export const initializeServices = (services: Services): void => {
    servicesInstance = services;
};
export { subscriptionService, paymentService };

