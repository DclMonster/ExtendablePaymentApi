import { PaymentProvider, PaymentStatus } from './payment';

/**
 * Base webhook event interface
 * @interface WebhookEvent
 */
export interface WebhookEvent {
  /** Event type */
  type: string;
  /** Event timestamp */
  timestamp: Date;
  /** Provider that sent the webhook */
  provider: PaymentProvider;
  /** Raw webhook data */
  data: Record<string, any>;
}

/**
 * Payment webhook event interface
 * @interface PaymentWebhookEvent
 * @extends WebhookEvent
 */
export interface PaymentWebhookEvent extends WebhookEvent {
  /** Payment ID */
  paymentId: string;
  /** New payment status */
  status: PaymentStatus;
}

/**
 * Webhook verification result
 * @interface WebhookVerificationResult
 */
export interface WebhookVerificationResult {
  /** Whether the webhook is valid */
  isValid: boolean;
  /** Error message if verification failed */
  error?: string;
}

/**
 * Webhook handler interface
 * @interface WebhookHandler
 */
export interface WebhookHandler {
  /** Verify webhook signature */
  verifySignature(request: Request): Promise<WebhookVerificationResult>;
  /** Process webhook event */
  processEvent(event: WebhookEvent): Promise<void>;
}

/**
 * Provider-specific webhook handlers
 */
export interface WebhookHandlers {
  paypal: WebhookHandler;
  coinbase: WebhookHandler;
  google: WebhookHandler;
  apple: WebhookHandler;
}

/**
 * Webhook configuration interface
 * @interface WebhookConfig
 */
export interface WebhookConfig {
  /** Endpoint URL */
  endpoint: string;
  /** Secret key for verification */
  secret: string;
  /** Additional provider-specific configuration */
  options?: Record<string, any>;
} 