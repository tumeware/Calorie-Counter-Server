from flask import Blueprint, request
from pymongo import MongoClient
from bson.json_util import dumps
import jwt
import os
import bcrypt
import datetime
from misc.stripeexpire import StripeExpireCheck

login = Blueprint('login', __name__)  # router

# security
token_key = os.environ.get('TOKEN_KEY')
mongo_url = os.environ.get('MONGODB_URI')

# MongoDB
client = MongoClient(mongo_url or 'mongodb://localhost:27017/')
db = client.magicpill
collection = db.users


@login.route("/login", methods=['POST'])
def newandget():
        newuser = request.get_json()['newuser']
        if newuser:
            password = request.get_json()['password']
            email = request.get_json()['email']
            hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            hashed = hashed.decode('UTF-8')
            exsist = collection.find_one({'email': email})

            if exsist:
                return dumps(False)
            else:
                collection.insert_one({'email': email, 'password': hashed})
                return dumps(True)
        else:
            finduser = ''
            password = request.get_json()['password']
            email = request.get_json()['email']

            if email and password:
                finduser = collection.find_one({'email': email})
            else:
                return dumps(False)

            if finduser:
                hash = finduser['password']
                id = finduser['_id']
                stripe_id = finduser['stripe_id']
                stripe = StripeExpireCheck(id)
                id = str(id)
                # expd = datetime.timedelta(days=30)
            else:
                return dumps(False)

            if password and email and stripe > 0:
                if bcrypt.checkpw(
                    password.encode('utf-8'), hash.encode('utf-8')
                ):
                    userdata = {'_id': id, 'stripe_id': stripe_id}
                    token = jwt.encode(userdata, token_key, algorithm='HS256')
                    token = token.decode('UTF-8')
                    return dumps({'token': token})
                else:
                    return dumps({'token': False})
            elif stripe < 0:
                return dumps({'expired': True})
            else:
                return dumps(False)


# password reset
@login.route("/login", methods=['PUT'])
def update():
    emailtoken = request.get_json()['emailtoken']
    newpass = request.get_json()['password']
    finduser = collection.find_one({'resetPasswordToken': emailtoken})
    timeNow = datetime.datetime.now()

    if finduser:
        resetPasswordExpires = finduser['resetPasswordExpires']
        resetPasswordExpires = int(resetPasswordExpires)
        timeThen = datetime.datetime.utcfromtimestamp(resetPasswordExpires)

        if timeThen >= timeNow:
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

        return dumps(True)

    else:
        return dumps(False)
