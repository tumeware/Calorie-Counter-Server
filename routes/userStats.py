from flask import Blueprint, request
from pymongo import MongoClient
from bson.json_util import dumps
from bson.objectid import ObjectId
import jwt
import os
import bcrypt
import datetime
from misc.stripeexpire import StripeExpireCheck

userStats = Blueprint('userStats', __name__)  # router

# security
token_key = os.environ.get('TOKEN_KEY')
mongo_url = os.environ.get('MONGODB_URI')

# MongoDB
client = MongoClient(mongo_url or 'mongodb://localhost:27017/')
db = client.magicpill
collection = db.userStats


# get
@userStats.route("/user-stats", methods=['POST'])
def get():
        token = request.get_json()['token']
        # language = request.get_json()['language']
        decoded = jwt.decode(token, token_key, algorithms='HS256')

        if decoded:
            id = decoded['_id']
            stripe = StripeExpireCheck(id)

            if stripe > 0:
                results = collection.find_one({'userId': decoded['_id']})
                return dumps(results)

            elif stripe < 0:
                return dumps({'expired': True})

            else:
                return dumps(False)
        else:
            return dumps(False)


#new item
@userStats.route("/user-stats-new-item", methods=['POST'])
def newItem():
    token = request.get_json()['token']
    itemId = request.get_json()['id']
    item = request.get_json()['item']
    decoded = jwt.decode(token, token_key, algorithms='HS256')

    if decoded:
        id = decoded['_id']
        stripe = StripeExpireCheck(id)

        if stripe > 0:
            collection.update_one({ "_id": ObjectId(itemId) },
                { "$push":
                    {
                        item
                    }
                },
                True
            )
            return dumps(True)

        elif stripe < 0:
            return dumps({'expired': True})

        return dumps(False)

    else:
        return dumps(False)


# new user weight (and kcal)
@userStats.route("/user-stats-new-user-weight-kcal", methods=['POST'])
def newUserWeightKcal():
    token = request.get_json()['token']
    weight = request.get_json()['weight']
    kcal = request.get_json()['kcal']
    decoded = jwt.decode(token, token_key, algorithms='HS256')

    if decoded:
        id = decoded['_id']
        stripe = StripeExpireCheck(id)

        if stripe > 0:
            collection.insert_one( { "userId" : id, "weight" : [ weight ], "kcal" : [ kcal ] } )
            return dumps(True)

        elif stripe < 0:
            return dumps({'expired': True})

        return dumps(False)

    else:
        return dumps(False)


#new weight item
@userStats.route("/user-stats-new-weight", methods=['POST'])
def newWeight():
    token = request.get_json()['token']
    itemId = request.get_json()['id']
    item = request.get_json()['item']
    decoded = jwt.decode(token, token_key, algorithms='HS256')

    if decoded:
        id = decoded['_id']
        stripe = StripeExpireCheck(id)

        if stripe > 0:
            collection.update_one({ "_id": ObjectId(itemId) },
                { "$push":
                    {
                        "weight": item
                    }
                },
                True
            )
            return dumps(True)

        elif stripe < 0:
            return dumps({'expired': True})

        return dumps(False)

    else:
        return dumps(False)


#new kcal
@userStats.route("/user-stats-new-kcal", methods=['POST'])
def newKcal():
    token = request.get_json()['token']
    itemId = request.get_json()['id']
    item = request.get_json()['item']
    decoded = jwt.decode(token, token_key, algorithms='HS256')

    if decoded:
        id = decoded['_id']
        stripe = StripeExpireCheck(id)

        if stripe > 0:
            collection.update_one({ "_id": ObjectId(itemId) },
                { "$push":
                    {
                        "kcal": item
                    }
                },
                True
            )
            return dumps(True)

        elif stripe < 0:
            return dumps({'expired': True})

        return dumps(False)

    else:
        return dumps(False)


#delete
@userStats.route("/user-stats", methods=['DELETE'])
def delete():
    token = request.get_json()['token']
    statid = request.get_json()['statid']
    # kcalid = request.get_json()['kcalid']
    weightid = request.get_json()['weightid']
    decoded = jwt.decode(token, token_key, algorithms='HS256')

    if decoded:
        id = decoded['_id']
        stripe = StripeExpireCheck(id)

        if stripe > 0:
            collection.update_one({ "_id": ObjectId(statid) },
                { "$pull":
                    {
                        # "kcal": { "_id": kcalid },
                        "weight": { "_id": weightid }
                    }
                },
                True
            )
            return dumps(True)

        elif stripe < 0:
            return dumps({'expired': True})

        return dumps(False)

    else:
        return dumps(False)
