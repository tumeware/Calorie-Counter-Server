from flask import Blueprint, request
from pymongo import MongoClient
from bson.json_util import dumps
import jwt
import os
import bcrypt
import datetime
from misc.stripeexpire import StripeExpireCheck

eatedFoods = Blueprint('eatedFoods', __name__)  # router

# security
token_key = os.environ.get('TOKEN_KEY')
mongo_url = os.environ.get('MONGODB_URI')

# MongoDB
client = MongoClient(mongo_url or 'mongodb://localhost:27017/')
db = client.magicpill
collection = db.eatedFoods


# get
@eatedFoods.route("/eated-foods", methods=['POST'])
def newandget():
        newfood = request.get_json()['newfood']
        if newfood:
            token = request.get_json()['token']
            food = request.get_json()['food']
            decoded = jwt.decode(token, token_key, algorithms='HS256')

            if decoded:
                id = decoded['_id']
                stripe = StripeExpireCheck(id)

                if stripe > 0:
                    collection.insert(food)
                    return dumps(True)

                elif stripe < 0:
                    return dumps({'expired': True})

                return dumps(False)

            else:
                return dumps(False)

        else:
            token = request.get_json()['token']
            ## language = request.get_json()['language']
            decoded = jwt.decode(token, token_key, algorithms='HS256')

            # return dumps(mongo_url) # test

            if decoded:
                results = collection.find({'userId': decoded['_id']})
                return dumps(results)
            else:
                return dumps(False)


# update
@eatedFoods.route("/eated-foods", methods=['PUT'])
def update():
    token = request.get_json()['token']
    foodId = request.get_json()['foodId']
    items = request.get_json()['items']
    decoded = jwt.decode(token, token_key, algorithms='HS256')

    if decoded:
        id = decoded['_id']
        stripe = StripeExpireCheck(id)

        if stripe > 0:
            collection.update_one({'_id': foodId}, {'$set': items})
            return dumps(True)

        elif stripe < 0:
            return dumps({'expired': True})

        return dumps(False)

    else:
        return dumps(False)


# delete
@eatedFoods.route("/eated-foods", methods=['DELETE'])
def delete():
    token = request.get_json()['token']
    foodId = request.get_json()['foodId']
    decoded = jwt.decode(token, token_key, algorithms='HS256')

    if decoded:
        id = decoded['_id']
        stripe = StripeExpireCheck(id)

        if stripe > 0:
            collection.delete_many({'_id': foodId})
            return dumps(True)

        elif stripe < 0:
            return dumps({'expired': True})

        return dumps(False)

    else:
        return dumps(False)
