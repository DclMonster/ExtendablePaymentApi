/**
 * Custom error class for webhook-related errors
 */
export class WebhookError extends Error {
    /**
     * Create a new webhook error
     * @param message - Error message
     * @param cause - Original error that caused this error
     */
    constructor(message: string, public readonly cause?: Error) {
        super(message);
        this.name = 'WebhookError';
        
        // Maintain proper stack trace
        if (Error.captureStackTrace) {
            Error.captureStackTrace(this, WebhookError);
        }

        // Set the prototype explicitly for better instanceof support
        Object.setPrototypeOf(this, WebhookError.prototype);
    }
} 