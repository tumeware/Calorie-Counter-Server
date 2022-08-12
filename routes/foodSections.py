from flask import Blueprint, request
from pymongo import MongoClient
from bson.json_util import dumps
from bson.objectid import ObjectId
import jwt
import os
import bcrypt
from misc.stripeexpire import StripeExpireCheck

foodSections = Blueprint('foodSections', __name__)  # router

# security
token_key = os.environ.get('TOKEN_KEY')
mongo_url = os.environ.get('MONGODB_URI')

# MongoDB
client = MongoClient(mongo_url or 'mongodb://localhost:27017/')
db = client.magicpill
collection = db.foodSections


# get
@foodSections.route("/food-sections", methods=['POST'])
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


# new user item
@foodSections.route("/new-user-food-section", methods=['POST'])
def newsection():
    token = request.get_json()['token']
    sections = request.get_json()['sections']
    decoded = jwt.decode(token, token_key, algorithms='HS256')

    if decoded:
        id = decoded['_id']
        stripe = StripeExpireCheck(id)

        if stripe > 0:
            collection.insert({
                "userId" : id,
                "sections" : sections
            })
            return dumps(True)

        elif stripe < 0:
            return dumps({'expired': True})

        return dumps(False)

    else:
        return dumps(False)


# new item
@foodSections.route("/new-food-section", methods=['POST'])
def new():
    token = request.get_json()['token']
    itemid = request.get_json()['itemid']
    item = request.get_json()['item']
    decoded = jwt.decode(token, token_key, algorithms='HS256')

    if decoded:
        id = decoded['_id']
        stripe = StripeExpireCheck(id)

        if stripe > 0:
            collection.update_one({ "_id": ObjectId(itemid) }, { "$push": {"sections": item}}, True)
            return dumps(True)

        elif stripe < 0:
            return dumps({'expired': True})

        return dumps(False)

    else:
        return dumps(False)


# update
@foodSections.route("/food-sections", methods=['PUT'])
def update():
    token = request.get_json()['token']
    sectionId = request.get_json()['sectionId']
    itemId = request.get_json()['itemId']
    name = request.get_json()['name']
    image = request.get_json()['image']
    decoded = jwt.decode(token, token_key, algorithms='HS256')

    if decoded:
        id = decoded['_id']
        stripe = StripeExpireCheck(id)

        if stripe > 0:
            collection.update_one(
                {
                    "_id" : ObjectId(sectionId),
                    "sections._id" : itemId
                },
                {
                    "$set": {
                        "sections.$.name" : name,
                        "sections.$.img" : image
                    }
                }
            )
            return dumps(True)

        elif stripe < 0:
            return dumps({'expired': True})

        return dumps(False)

    else:
        return dumps(False)


# delete
@foodSections.route("/food-sections", methods=['DELETE'])
def delete():
    token = request.get_json()['token']
    sectionId = request.get_json()['sectionId']
    itemId = request.get_json()['itemId']
    decoded = jwt.decode(token, token_key, algorithms='HS256')

    if decoded:
        id = decoded['_id']
        stripe = StripeExpireCheck(id)

        if stripe > 0:
            collection.update_one({ "_id": ObjectId(sectionId) }, { "$pull": {"sections": {"_id": itemId}}})
            return dumps(True)

        elif stripe < 0:
            return dumps({'expired': True})

        return dumps(False)

    else:
        return dumps(False)
