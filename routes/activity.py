from flask import Blueprint, request
from pymongo import MongoClient
from bson.json_util import dumps
import jwt
import os
import bcrypt
import datetime
from misc.stripeexpire import StripeExpireCheck

activity = Blueprint('activity', __name__)  # router

# security
token_key = os.environ.get('TOKEN_KEY')
mongo_url = os.environ.get('MONGODB_URI')

# MongoDB #
client = MongoClient(mongo_url or 'mongodb://localhost:27017/')
db = client.magicpill
collection = db.activity


# get
@activity.route("/activity", methods=['POST'])
def getactivity():
        token = request.get_json()['token']
        # language = request.get_json()['language']
        decoded = jwt.decode(token, token_key, algorithms='HS256')

        if decoded:
            results = collection.find({'userId': decoded['_id']})
            return dumps(results)
        else:
            return dumps(False)


# new
@activity.route("/new-activity", methods=['POST'])
def newactivity():
        token = request.get_json()['token']
        activity = request.get_json()['activity']
        decoded = jwt.decode(token, token_key, algorithms='HS256')

        if decoded:
            id = decoded['_id']
            stripe = StripeExpireCheck(id)

            if stripe > 0:
                collection.insert(activity)
                return dumps(True)

            elif stripe < 0:
                return dumps({'expired': True})

            return dumps(False)

        else:
            return dumps(False)


# update
@activity.route("/activity", methods=['PUT'])
def updateactivity():
    token = request.get_json()['token']
    activityId = request.get_json()['activityId']
    items = request.get_json()['items']
    decoded = jwt.decode(token, token_key, algorithms='HS256')

    if decoded:
        id = decoded['_id']
        stripe = StripeExpireCheck(id)

        if stripe > 0:
            collection.update_one({'_id': activityId}, {'$set': items})
            return dumps(True)

        elif stripe < 0:
            return dumps({'expired': True})

        return dumps(False)

    else:
        return dumps(False)


# delete
@activity.route("/activity", methods=['DELETE'])
def deleteactivity():
        token = request.get_json()['token']
        activityId = request.get_json()['activityId']
        decoded = jwt.decode(token, token_key, algorithms='HS256')

        if decoded:
            id = decoded['_id']
            stripe = StripeExpireCheck(id)

            if stripe > 0:
                collection.delete_many({'_id': activityId})
                return dumps(True)

            elif stripe < 0:
                return dumps({'expired': True})

            return dumps(False)

        else:
            return dumps(False)
