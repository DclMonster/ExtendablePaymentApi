/**
 * Simple logger utility for consistent logging across the application
 */
export class Logger {
    /**
     * Log an info message
     * @param message - The message to log
     * @param args - Additional arguments to log
     */
    public static info(message: string, ...args: any[]): void {
        console.log(`[INFO] ${message}`, ...args);
    }

    /**
     * Log an error message
     * @param message - The message to log
     * @param args - Additional arguments to log
     */
    public static error(message: string, ...args: any[]): void {
        console.error(`[ERROR] ${message}`, ...args);
    }

    /**
     * Log a warning message
     * @param message - The message to log
     * @param args - Additional arguments to log
     */
    public static warn(message: string, ...args: any[]): void {
        console.warn(`[WARN] ${message}`, ...args);
    }

    /**
     * Log a debug message
     * @param message - The message to log
     * @param args - Additional arguments to log
     */
    public static debug(message: string, ...args: any[]): void {
        if (process.env.NODE_ENV !== 'production') {
            console.debug(`[DEBUG] ${message}`, ...args);
        }
    }
} 