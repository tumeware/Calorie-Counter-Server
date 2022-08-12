from flask import Blueprint, request
from pymongo import MongoClient
from bson.json_util import dumps
import jwt
import os
import bcrypt
import datetime
from misc.stripeexpire import StripeExpireCheck

userInfo = Blueprint('userInfo', __name__)  # router

# security
token_key = os.environ.get('TOKEN_KEY')
mongo_url = os.environ.get('MONGODB_URI')

# MongoDB
client = MongoClient(mongo_url or 'mongodb://localhost:27017/')
db = client.magicpill
collection = db.userInfo


# get
@userInfo.route("/user-info", methods=['POST'])
def get():
        token = request.get_json()['token']
        decoded = jwt.decode(token, token_key, algorithms='HS256')

        if decoded:
            id = decoded['_id']
            stripe = StripeExpireCheck(id)

            if stripe > 0:
                results = collection.find({'userId': decoded['_id']})
                return dumps(results)

            elif stripe < 0:
                return dumps({'expired': True})

            else:
                return dumps(False)
        else:
            return dumps(False)

# new
@userInfo.route("/new-user-info", methods=['POST'])
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
                    "height" : items['height'],
                    "gender" : items['gender'],
                    "age" : items['age'],
                    "waist" : items['waist'],
                    "pelvis" : items['pelvis'],
                    "neck" : items['neck'],
                    "goalKg" : items['goalKg'],
                    "mode" : items['mode']
                })
                return dumps(True)

            elif stripe < 0:
                return dumps({'expired': True})

            return dumps(False)

        else:
            return dumps(False)


# update
@userInfo.route("/user-info", methods=['PUT'])
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
