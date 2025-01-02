import { SubscriptionService } from './subscriptionService';
import { PaymentService } from './paymentService';

const subscriptionService = new SubscriptionService();
const paymentService = new PaymentService();

export { subscriptionService, paymentService };
