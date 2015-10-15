__author__ = 'mudassir'

import sys
import os
import requests
import json

from flask import Flask
from flask import request, redirect
from flask_cors.extension import CORS
from flask_sslify import SSLify

from GoAPICalls.goibibo import giveCommonResponse
sys.path.append("../")

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)
app.requests_session = requests.Session()
app.secret_key = os.urandom(24)

sslify = SSLify(app)


def getFormattedText(string):
    return string.replace("\n","").replace("\r","").strip()

@app.route("/getAllDetails",methods=['GET','POST'])
def details():
    source = getFormattedText(request.args.get('source'))
    destination = getFormattedText(request.args.get('destination'))
    date = getFormattedText(request.args.get('date'))

    if(source and destination and date):
        resp = giveCommonResponse(source,destination,date)
        return json.dumps({
            "status_code":200,
            "result":resp,
        })
        pass
    else:
        return json.dumps({
            "status_code":400,
            "error":"Not all arguments are passed",
        })



