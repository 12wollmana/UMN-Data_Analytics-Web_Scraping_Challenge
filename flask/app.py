from flask import Flask, render_template, redirect
from flask_pymongo import PyMongo
from datetime import datetime
import time

import sys
sys.path.append("../scrape")
from scrape_mars import scrape

sys.path.append("..")
from config import mongo_uri

app = Flask(__name__)

app.config["MONGO_URI"] = mongo_uri
mongo = PyMongo(app)

def utc2local(utc):
    """
    Converts from UTC to local time.
    From https://stackoverflow.com/questions/4770297/convert-utc-datetime-string-to-local-datetime.

    Parameters
    ----------
    utc : [DateTime]
        A UTC DateTime to convert.

    Returns
    -------
    [DateTime]
        A local DateTime.
    """
    epoch = time.mktime(utc.timetuple())
    offset = datetime.fromtimestamp (epoch) - datetime.utcfromtimestamp (epoch)
    return utc + offset

@app.route("/")
def index():
    last_update = "Never"
    has_data = False
    mars_data = mongo.db.mars_data.find_one()
    if(mars_data):
        has_data = True
        last_update_utc = mars_data["last_update_utc"]
        if(last_update_utc):
            last_update = utc2local(last_update_utc).strftime("%m/%d/%Y, %I:%M %p")
   
    return render_template("index.html", 
                            has_data = has_data,
                            data=mars_data, 
                            last_update = last_update)


@app.route("/scrape")
def scraper():
    mars_data_db = mongo.db.mars_data
    mars_data = scrape()
    mars_data["last_update_utc"] = datetime.utcnow()
    mars_data_db.update({}, mars_data, upsert=True)
    return redirect("/", code=302)

@app.route("/clear")
def clear():
    mars_data_db = mongo.db.mars_data
    mars_data_db.delete_many({})
    return redirect("/", code=302)

if __name__ == "__main__":
    app.run(debug=True)