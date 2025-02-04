/**
 * Payment provider implementations.
 *
 * This module contains concrete implementations of various payment providers
 * including PayPal, Stripe, and Coinbase.
 */

/**
 * Base class for payment providers.
 *
 * This class serves as the abstract base class for all payment provider
 * implementations. It defines the interface that all payment providers must
 * implement.
 *
 * Parameters
 * ----------
 * apiKey : string
 *     The API key for the payment provider.
 * merchantId : string
 *     The merchant ID for the payment provider.
 * environment : 'sandbox' | 'production'
 *     The environment to use for the payment provider.
 *
 * Attributes
 * ----------
 * providerName : string
 *     The name of the payment provider.
 * supportedCurrencies : Set<string>
 *     Set of supported currency codes.
 * webhookHandler : WebhookHandler
 *     Handler for processing webhook events.
 *
 * Notes
 * -----
 * All payment providers must implement the following methods:
 * - createPayment
 * - processWebhook
 * - verifySignature
 */
export abstract class PaymentProvider {
  protected readonly apiKey: string;
  protected readonly merchantId: string;
  protected readonly environment: 'sandbox' | 'production';

  /**
   * Create a new payment.
   *
   * Parameters
   * ----------
   * amount : number
   *     The payment amount.
   * currency : string
   *     The three-letter currency code (ISO 4217).
   * description : string, optional
   *     A description of the payment.
   *
   * Returns
   * -------
   * Promise<PaymentResponse>
   *     The response containing payment details and status.
   *
   * Raises
   * ------
   * InvalidCurrencyError
   *     If the currency is not supported.
   * PaymentProviderError
   *     If there's an error communicating with the payment provider.
   *
   * See Also
   * --------
   * processWebhook : Method for handling webhook notifications
   * PaymentResponse : Interface containing payment response details
   *
   * Examples
   * --------
   * ```typescript
   * const provider = new PayPalProvider({
   *   apiKey: "key",
   *   merchantId: "id"
   * });
   * const response = await provider.createPayment({
   *   amount: 100.00,
   *   currency: "USD",
   *   description: "Test payment"
   * });
   * console.log(response.status); // PaymentStatus.PENDING
   * ```
   */
  abstract createPayment(
    amount: number,
    currency: string,
    description?: string
  ): Promise<PaymentResponse>;

  /**
   * Process a webhook event from the payment provider.
   *
   * Parameters
   * ----------
   * event : WebhookEvent
   *     The webhook event to process.
   *
   * Returns
   * -------
   * Promise<WebhookResponse>
   *     The response indicating the result of processing.
   *
   * Raises
   * ------
   * InvalidSignatureError
   *     If the webhook signature is invalid.
   * UnknownEventTypeError
   *     If the event type is not recognized.
   *
   * Notes
   * -----
   * This method should:
   * 1. Verify the webhook signature
   * 2. Parse the event data
   * 3. Update the payment status
   * 4. Trigger any necessary callbacks
   *
   * See Also
   * --------
   * verifySignature : Method for verifying webhook signatures
   * WebhookEvent : Interface containing webhook event details
   */
  abstract processWebhook(event: WebhookEvent): Promise<WebhookResponse>;

  /**
   * Verify the signature of a webhook payload.
   *
   * Parameters
   * ----------
   * payload : Buffer
   *     The raw webhook payload.
   * signature : string
   *     The signature provided in the webhook headers.
   *
   * Returns
   * -------
   * Promise<boolean>
   *     True if the signature is valid, False otherwise.
   *
   * Notes
   * -----
   * Each payment provider implements their own signature verification
   * algorithm. Common approaches include:
   * - HMAC with SHA-256
   * - RSA signatures
   * - Ed25519 signatures
   */
  abstract verifySignature(payload: Buffer, signature: string): Promise<boolean>;
} 