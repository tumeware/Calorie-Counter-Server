from flask import Flask, Blueprint, request, render_template, url_for
from pymongo import MongoClient
from bson.json_util import dumps
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from flask_cors import CORS
import os
import random
import string
from datetime import datetime, timedelta


# routes #
from routes.login import login
from routes.foods import foods
from routes.mets import mets
from routes.eatedFoods import eatedFoods
from routes.foodSections import foodSections
from routes.userInfo import userInfo
from routes.userSettings import userSettings
from routes.stripe import stripe_api
from routes.userStats import userStats
from routes.favorites import favorites
from routes.activity import activity


# app init
app = Flask(__name__, template_folder='mails', static_folder='static')
CORS(app)


# register routes
app.register_blueprint(login)
app.register_blueprint(foods)
app.register_blueprint(mets)
app.register_blueprint(eatedFoods)
app.register_blueprint(foodSections)
app.register_blueprint(userInfo)
app.register_blueprint(userSettings)
app.register_blueprint(stripe_api)
app.register_blueprint(userStats)
app.register_blueprint(favorites)
app.register_blueprint(activity)


# email variables
mailpassword = os.environ.get('MAIL_PASSWORD')
mailusername = os.environ.get('MAIL_USERNAME')
maildefaultsender = os.environ.get('MAIL_DEFAULT_SENDER')
mailServer = 'ssl0.ovh.net'
mailServerPort = 465


# mongo variables
mongo_url = os.environ.get('MONGODB_URI')
client = MongoClient(mongo_url or 'mongodb://localhost:27017/')
db = client.magicpill
collection = db.users


# random string generator
def randomString(stringLength=50):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))


# test route
@app.route('/')
def display():
    return "Yeah!"


# send reset password mail
@app.route("/reset-password", methods=['POST'])
def sendresetemail():
        email = request.get_json()['email']
        results = collection.find_one({'email': email})

        if results:
            someString = randomString()
            makeTime = datetime.now() + timedelta(hours=2)
            exp_date = makeTime.timestamp()

            collection.update_one({ "email": email }, { "$set": {"resetPasswordToken": someString, "resetPasswordExpires": exp_date}}, True)

            url = "https://my.magicpill.app/#/restore-password/" + someString

            msg = MIMEMultipart('alternative')
            msg['Subject'] = "Reset your Password - Magicpill.app"
            msg['From'] = maildefaultsender
            msg['To'] = email

            text = "Reset your password\n Copy and paste the following link in your browser:\n " + url + "\n The link is valid for 2 hours.\n If you didn't request a new password, you can safely delete this email.\n Cheers\n Magicpill Team"
            html = render_template("reset-password.html", url=url, image="cid:image1")

            part1 = MIMEText(text, 'plain')
            part2 = MIMEText(html, 'html')
            image = open('static/img/logo.png', 'rb')
            part3 = MIMEImage(image.read())
            part3.add_header('Content-ID', '<image1>')
            image.close()
            msg.attach(part1)
            msg.attach(part2)
            msg.attach(part3)

            s = smtplib.SMTP_SSL(mailServer, mailServerPort)
            s.login(mailusername, mailpassword)
            s.sendmail(maildefaultsender, email, msg.as_string())
            s.quit()

            return dumps(True)
        else:
            return dumps(False)


# run server
if __name__ == '__main__':
    app.run()
    #app.run(debug=True, host='0.0.0.0', port=3134) # local only!
