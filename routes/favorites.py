from flask import Blueprint, request
from pymongo import MongoClient
from bson.json_util import dumps
import jwt
import os
import bcrypt
import datetime
from misc.stripeexpire import StripeExpireCheck

favorites = Blueprint('favorites', __name__)  # router

# security
token_key = os.environ.get('TOKEN_KEY')
mongo_url = os.environ.get('MONGODB_URI')

# MongoDB
client = MongoClient(mongo_url or 'mongodb://localhost:27017/')
db = client.magicpill
collection = db.favorites


# get
@favorites.route("/favorites", methods=['POST'])
def get():
        token = request.get_json()['token']
        decoded = jwt.decode(token, token_key, algorithms='HS256')

        if decoded:
            results = collection.find({'userId': decoded['_id']})
            return dumps(results)
        else:
            return dumps(False)


# new user item
@favorites.route("/new-user-favorites", methods=['POST'])
def newuserfavorites():
    token = request.get_json()['token']
    _id = request.get_json()['_id']
    decoded = jwt.decode(token, token_key, algorithms='HS256')

    if decoded:
        id = decoded['_id']
        stripe = StripeExpireCheck(id)

        if stripe > 0:
            collection.insert({
                "_id" : _id,
                "userId" : id,
                "foods" : [],
                "activities" : []
            })
            return dumps(True)

        elif stripe < 0:
            return dumps({'expired': True})

        return dumps(False)

    else:
        return dumps(False)


# new
@favorites.route("/new-favorite", methods=['POST'])
def new():
        token = request.get_json()['token']
        itemid = request.get_json()['itemid']
        items = request.get_json()['items']
        decoded = jwt.decode(token, token_key, algorithms='HS256')

        if decoded:
            id = decoded['_id']
            stripe = StripeExpireCheck(id)

            if stripe > 0:
                collection.update_one({'_id': itemid}, {'$push': items}, True)
                return dumps(True)

            elif stripe < 0:
                return dumps({'expired': True})

            return dumps(False)

        else:
            return dumps(False)


# update
@favorites.route("/favorites", methods=['PUT'])
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


# delete
@favorites.route("/favorites", methods=['DELETE'])
def delete():
    token = request.get_json()['token']
    itemid = request.get_json()['itemid']
    deleteditemid = request.get_json()['deleteditemid']
    decoded = jwt.decode(token, token_key, algorithms='HS256')

    if decoded:
        id = decoded['_id']
        stripe = StripeExpireCheck(id)

        if stripe > 0:
            collection.update({ "_id": itemid }, { "$pull": deleteditemid })
            return dumps(True)

        elif stripe < 0:
            return dumps({'expired': True})

        return dumps(False)

    else:
        return dumps(False)
