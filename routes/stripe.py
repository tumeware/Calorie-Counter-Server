from flask import Blueprint, request, Response
from bson.json_util import dumps
import stripe
import os
from pymongo import MongoClient
import datetime
import jwt


# route
stripe_api = Blueprint('stripe_api', __name__)  # router


# env variables
stripe.api_key = os.environ.get('STRIPE_KEY')
endpoint_secret = os.environ.get('STRIPE_WEBHOOKS_SECRET')
mongo_url = os.environ.get('MONGODB_URI')
token_key = os.environ.get('TOKEN_KEY')


# MongoDB
client = MongoClient(mongo_url or 'mongodb://localhost:27017/')
db = client.magicpill
collection = db.users


# new customer
@stripe_api.route("/stripe-api", methods=['POST'])
def addnew():
    email = request.get_json()['email']
    success_url = request.get_json()['success_url']
    cancel_url = request.get_json()['cancel_url']
    plan = request.get_json()['plan']

    customer = stripe.Customer.create(
        email = email
    )

    subscription = stripe.checkout.Session.create(
        customer = customer.id,
        payment_method_types = ['card'],
        subscription_data = {
            'items': [{
                'plan': plan,
            }],
            'trial_period_days': 7
        },
        success_url = success_url,
        cancel_url = cancel_url
    )

    return dumps(subscription.id)

# make customer portal token (session)
@stripe_api.route("/stripe-customer-portal", methods=['POST'])
def customerportalsession():
    token = request.get_json()['token']
    decoded = jwt.decode(token, token_key, algorithms='HS256')
    customer_id = decoded['stripe_id']
    return_url = request.get_json()['return_url']

    if decoded:
        newportalsession = stripe.billing_portal.Session.create(
            customer = customer_id,
            return_url = return_url
        )

        return dumps(newportalsession.url)
    else:
        return dumps(False)


# webhooks
@stripe_api.route("/stripe-webhooks", methods=['GET', 'POST'])
def webhooks():
    payload =  request.data
    sig_header = request.headers['STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        return Response(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return Response(status=400)

    if event.type == 'invoice.payment_succeeded':
        data = event.data.object
        origTime = datetime.datetime.fromtimestamp(data.lines.data[0].period.end)
        newTime = origTime + datetime.timedelta(days=2)
        newTime = newTime.timestamp()

        collection.update_one(
            {
                'email': data.customer_email
            },
            {
                '$set': {
                    'stripe_current_period_end_time': newTime,
                    'stripe_id': data.customer
                }
            }, True
        )

    elif event.type == 'payment_method.attached':
        data = event.data.object

        collection.update_one(
            {
                'email': data.billing_details.email
            },
            {
                '$set': {
                    'stripe_card_last_four': data.card.last4,
                    'stripe_card_brand': data.card.brand
                }
            }
        )

    else:
        return Response(status=400)

    return Response(status=200)
