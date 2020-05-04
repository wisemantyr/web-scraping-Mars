from flask import Flask, render_template, redirect
import pymongo
import scrape_mars

app = Flask(__name__)

# Create connection variable
conn = 'mongodb://localhost:27017'

# Pass connection to the pymongo instance.
client = pymongo.MongoClient(conn)

# Connect to a database. Will create one if not already available.
db = client.mars_db


@app.route("/scrape")
def scrape():
    scrape_mars.scrape_mars()
    return redirect("/")

@app.route("/")
def home():
    mars_data = db.mars_data.find_one()
    return render_template ("index.html", mars_data = mars_data)

if __name__ == "__main__":
    app.run(debug=True)