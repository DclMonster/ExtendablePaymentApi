/**
 * Supported payment providers
 */
export type PaymentProvider = 'paypal' | 'coinbase' | 'google' | 'apple';

/**
 * Payment status types
 */
export type PaymentStatus = 'pending' | 'completed' | 'failed';

/**
 * Payment request interface
 * @interface PaymentRequest
 */
export interface PaymentRequest {
  /** Payment provider to use */
  provider: PaymentProvider;
  /** Payment amount */
  amount: number;
  /** Currency code (e.g., 'USD') */
  currency: string;
  /** Payment description */
  description: string;
  /** Optional metadata */
  metadata?: Record<string, any>;
}

/**
 * Payment response interface
 * @interface PaymentResponse
 */
export interface PaymentResponse {
  /** Unique payment identifier */
  id: string;
  /** Current payment status */
  status: PaymentStatus;
  /** Payment provider used */
  provider: PaymentProvider;
  /** Payment amount */
  amount: number;
  /** Currency code */
  currency: string;
  /** Creation timestamp */
  createdAt: Date;
  /** Last update timestamp */
  updatedAt: Date;
  /** Optional metadata */
  metadata?: Record<string, any>;
}

/**
 * Payment error types
 */
export class PaymentError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'PaymentError';
  }
}

export class PaymentProviderError extends PaymentError {
  constructor(message: string) {
    super(message);
    this.name = 'PaymentProviderError';
  }
}

export class ValidationError extends PaymentError {
  constructor(message: string) {
    super(message);
    this.name = 'ValidationError';
  }
} 