from flask_restful import Resource, reqparse
from flask import Response
from ...services import get_services, PaymentProvider, ItemType, OneTimePaymentData, SubscriptionPaymentData, Services
from typing import Dict, Any

post_args = reqparse.RequestParser()
post_args.add_argument('user_id', type=str, required=True, help='The user ID')
post_args.add_argument('item_category', type=str, required=True, help='The item category')
post_args.add_argument('payment_provider', type=str, required=True, help='The payment provider')
post_args.add_argument('payment_type', type=str, required=True, help='The payment type')
post_args.add_argument('purchase_id', type=str, required=True, help='The purchase ID')

class CreditPurchase(Resource):

    def __init__(self) -> None:
        self._services: Services[Any, Any] = get_services()

    def post(self) -> Response:
        args: Dict[str, Any] = post_args.parse_args()
        user_id: str = args['user_id']
        item_category: str = args['item_category']
        payment_provider: PaymentProvider = PaymentProvider(args['payment_provider'])
        payment_type: str = args['payment_type']
        if payment_type == ItemType.ONE_TIME_PAYMENT:
            self._services._handle_one_time_payment(payment_provider, OneTimePaymentData(
                user_id=user_id,
                item_category=item_category,
                purchase_id=args['purchase_id'],
                item_name=args['item_name'],
                time_bought=args['time_bought'],
                status=args['status'],
                quantity=args['quantity']
            ))
        elif payment_type == ItemType.SUBSCRIPTION:
            self._services._handle_subscription(payment_provider, SubscriptionPaymentData(
                user_id=user_id,
                item_category=item_category,
                purchase_id=args['purchase_id'],
                item_name=args['item_name'],
                time_bought=args['time_bought'],
                status=args['status'],
            ))
        return Response(status=200)

