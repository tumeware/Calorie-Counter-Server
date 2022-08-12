from flask import Blueprint, request
from pymongo import MongoClient
from bson.json_util import dumps
import jwt
import os
import bcrypt
import datetime
from misc.stripeexpire import StripeExpireCheck

userSettings = Blueprint('userSettings', __name__)  # router

# security
token_key = os.environ.get('TOKEN_KEY')
mongo_url = os.environ.get('MONGODB_URI')

# MongoDB
client = MongoClient(mongo_url or 'mongodb://localhost:27017/')
db = client.magicpill
collection = db.userSettings


# get
@userSettings.route("/user-settings", methods=['POST'])
def get():
        token = request.get_json()['token']
        # language = request.get_json()['language']
        decoded = jwt.decode(token, token_key, algorithms='HS256')

        if decoded:
            results = collection.find({'userId': decoded['_id']})
            return dumps(results)
        else:
            return dumps(False)


# new
@userSettings.route("/new-user-settings", methods=['POST'])
def new():
        token = request.get_json()['token']
        items = request.get_json()['items']
        decoded = jwt.decode(token, token_key, algorithms='HS256')

        if decoded:
            id = decoded['_id']
            stripe = StripeExpireCheck(id)

            if stripe > 0:
                collection.insert({
                    "_id" : items['_id'],
                    "userId" : id,
                    "dietType" : items['dietType'],
                    "lbs" : items['lbs'],
                    "macros" : items['macros']
                })
                return dumps(True)

            elif stripe < 0:
                return dumps({'expired': True})

            return dumps(False)

        else:
            return dumps(False)


# update
@userSettings.route("/user-settings", methods=['PUT'])
def update():
    token = request.get_json()['token']
    itemId = request.get_json()['itemId']
    items = request.get_json()['items']
    decoded = jwt.decode(token, token_key, algorithms='HS256')

    if decoded:
        id = decoded['_id']
        stripe = StripeExpireCheck(id)

        if stripe > 0:
            collection.update_one({'_id': itemId}, {'$set': items})
            return dumps(True)

        elif stripe < 0:
            return dumps({'expired': True})

        return dumps(False)

    else:
        return dumps(False)
