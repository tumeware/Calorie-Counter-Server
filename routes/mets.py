from flask import Blueprint, request
from pymongo import MongoClient
from bson.json_util import dumps
import jwt
import os
import bcrypt
import datetime
from misc.stripeexpire import StripeExpireCheck

mets = Blueprint('mets', __name__)  # router

# security
token_key = os.environ.get('TOKEN_KEY')
mongo_url = os.environ.get('MONGODB_URI')

# MongoDB
client = MongoClient(mongo_url or 'mongodb://localhost:27017/')
db = client.magicpill
collection = db.mets


@mets.route("/mets", methods=['POST'])
def get():
        token = request.get_json()['token']
        query = request.get_json()['q']
        decoded = jwt.decode(token, token_key, algorithms='HS256')
        skip = request.get_json()['skip']
        limit = request.get_json()['limit']

        if decoded:
            id = decoded['_id']
            stripe = StripeExpireCheck(id)

            if stripe > 0:
                results = collection.find({'$text': {
                    '$search': query
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
