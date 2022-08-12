from flask import Blueprint, request
from pymongo import MongoClient
from bson.json_util import dumps
import jwt
import os
import bcrypt
import datetime
from misc.stripeexpire import StripeExpireCheck

foods = Blueprint('foods', __name__)  # router

# security
token_key = os.environ.get('TOKEN_KEY')
mongo_url = os.environ.get('MONGODB_URI')

# MongoDB
client = MongoClient(mongo_url or 'mongodb://localhost:27017/')
db = client.magicpill
collection = db.foods


@foods.route("/foods", methods=['POST'])
def newandget():
        newfood = request.get_json()['newfood']

        if newfood:
            token = request.get_json()['token']
            food = request.get_json()['food']
            decoded = jwt.decode(token, token_key, algorithms='HS256')

            if decoded:
                collection.insert_one(food)
                return dumps(True)
            else:
                return dumps(False)

        else:
            token = request.get_json()['token']
            query = request.get_json()['q']
            # language = request.get_json()['language']
            decoded = jwt.decode(token, token_key, algorithms='HS256')
            skip = request.get_json()['skip']
            limit = request.get_json()['limit']

            if decoded:
                id = decoded['_id']
                stripe = StripeExpireCheck(id)

                if stripe > 0:
                    results = collection.find({'$text': {
                        '$search': query,
                        # '$language': language
                    }}, {
                            'score': {
                                '$meta': 'textScore'
                            }
                        }
                    ).sort([('score', {'$meta': 'textScore'})]).skip(skip).limit(limit)
                    return dumps(results)

                elif stripe < 0:
                    return dumps({'expired': True})

                else:
                    return dumps(False)

            else:
                return dumps(False)

            return dumps(False)


@foods.route("/foods", methods=['PUT'])
def update():
    emailtoken = request.get_json()['emailtoken']
    newpass = request.get_json()['password']
    finduser = collection.find_one({'resetPasswordToken': emailtoken})
    resetPasswordExpires = finduser['resetPasswordExpires']

    if finduser and resetPasswordExpires >= datetime.datetime.utcnow():
        hashed = bcrypt.hashpw(newpass.encode('utf-8'), bcrypt.gensalt())
        hashed = hashed.decode('UTF-8')

        collection.update_one(
            {
                'resetPasswordToken': emailtoken
            },
            {
                '$set': {
                    'password': hashed
                }
            })
        return dumps(True)
    else:
        return dumps(False)
