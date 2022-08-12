import datetime
from pymongo import MongoClient
from bson.objectid import ObjectId
import os

# MongoDB variants
mongo_url = os.environ.get('MONGODB_URI')
client = MongoClient(mongo_url or 'mongodb://localhost:27017/')
db = client.magicpill
collection = db.users

class StripeExpireCheck:

    def __new__(self, id):
        self.id = id

        database = collection.find_one({'_id': ObjectId(id)})

        stripetime = database['stripe_current_period_end_time']
        stripetime = int(stripetime)

        a = datetime.datetime.today()
        b = datetime.datetime.utcfromtimestamp(stripetime)
        date1 = datetime.datetime(a.year, a.month, a.day, a.hour, a.minute, a.second)
        date2 = datetime.datetime(b.year, b.month, b.day, b.hour, b.minute, b.second)
        timeresult = (date2 - date1).total_seconds() / 60.0

        return timeresult
