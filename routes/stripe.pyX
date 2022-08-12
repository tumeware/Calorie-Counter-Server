from flask import Blueprint, request, Response
from bson.json_util import dumps
import stripe
import os
from pymongo import MongoClient
import datetime


# route
stripe_api = Blueprint('stripe_api', __name__)  # router


# env variables
stripe.api_key = os.environ.get('STRIPE_KEY')
endpoint_secret = os.environ.get('STRIPE_WEBHOOKS_SECRET')
mongo_url = os.environ.get('MONGODB_URI')


# MongoDB
client = MongoClient(mongo_url or 'mongodb://localhost:27017/')
db = client.magicpill
collection = db.users


# new customer
@stripe_api.route("/stripe-api", methods=['POST'])
def addnew():
    customer = stripe.Customer.create(
      description=request.get_json()['description'],
      source=request.get_json()['token'],
      email=request.get_json()['email']
    )

    subscription = stripe.Subscription.create(
      customer=customer.id,
      items=[{"plan": "plan_EShDuEUH4JednD"}],
      trial_period_days=7
    )

    collection.update_one(
        {
            'email': customer.email
        },
        {
            '$set': {
                'stripe_id': subscription.customer,
                'stripe_card_last_four': customer.sources.data[0].last4,
                'stripe_card_brand': customer.sources.data[0].brand
            }
        }
    )

    return dumps(True)


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
                'stripe_id': data.customer
            },
            {
                '$set': {
                    'stripe_current_period_end_time': newTime
                }
            }
        )

    elif event.type == 'invoice.payment_action_required':
        data = event.data.object
        print(data)

    else:
        return Response(status=400)

    return Response(status=200)
