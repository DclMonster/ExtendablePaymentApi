from flask_restful import Resource, reqparse
from .. import _services
from ...services import PaymentProvider

post_args = reqparse.RequestParser()
post_args.add_argument('user_id', type=str, required=True, help='The user ID')
post_args.add_argument('item_id', type=str, required=True, help='The item ID')
post_args.add_argument('item_category', type=str, required=True, help='The item category')
post_args.add_argument('payment_provider', type=str, required=True, help='The payment provider')




class CreditPurchase(Resource):

    def post(self):
        args = post_args.parse_args()
        user_id = args['user_id']
        item_id = args['item_id']
        item_category = args['item_category']
        payment_provider = args['payment_provider']
        match payment_provider.value:
            case PaymentProvider.APPLE:
                _services.on_apple_payment(user_id, item_id, item_category)
            case PaymentProvider.GOOGLE:
                _services.on_google_payment(user_id, item_id, item_category)
            case PaymentProvider.PAYPAL:
                _services.on_paypal_payment(user_id, item_id, item_category)
            case PaymentProvider.COINBASE:
                _services.on_coinbase_payment(user_id, item_id, item_category)
            case PaymentProvider.COINSUB:
                _services.on_coinsub_payment(user_id, item_id, item_category)

