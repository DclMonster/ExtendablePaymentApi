from .payment_service import PaymentService
from .subscription.apple_subscription_service import AppleSubscriptionService
from .subscription.google_subscription_service import GoogleSubscriptionService
from .subscription.coinbase_subscription_service import CoinbaseSubscriptionService

# Singleton instance of PaymentService
payment_service = PaymentService()

# Singleton instances of SubscriptionServices
apple_subscription_service = AppleSubscriptionService()
google_subscription_service = GoogleSubscriptionService()
coinbase_subscription_service = CoinbaseSubscriptionService()