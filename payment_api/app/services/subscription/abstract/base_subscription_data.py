from typing import TypedDict
class BaseSubscriptionData(TypedDict):
    provider: str
    user_id: str
    subscription_data: dict