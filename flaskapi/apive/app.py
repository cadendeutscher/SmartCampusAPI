from flask import Flask, abort, request, redirect, render_template, request, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from models import db

app = Flask(__name__)
 
db = SQLAlchemy()

login = LoginManager()

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///<db_name>.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)


#Allowed IP address for input
trusted_proxies = ('42.42.42.42', '82.42.82.42', '127.0.0.1')


#Credit to https://stackoverflow.com/questions/22251038/how-to-limit-access-to-flask-for-a-single-ip-address for the below code
#Determines if the ip address is in the list of allowed IP addresses
def limit_remote_addr():
    remote = request.remote_addr
    route = list(request.access_route)
    while remote in trusted_proxies:
        remote = route.pop()

    if remote != '10.20.30.40':
        abort(403)  # Forbidden

#HomeRoute For Application
@app.route("/")
def hello_world():
    return render_template("main_page.html")

#Sign-in for admin    
@app.route("/signin", methods = ['POST', 'GET'])
def sign_in():
    return render_template("signin.html")

#Query Sensor Data Return JSON for specific time line
@app.route("/<sensor>/<dayf>/<monthf>/yearf>/<dayt>/<montht>/yeart>")
def getSpecificData(sensor,dayf,monthf,yearf,dayt,montht,yeart):
    return "Successful retrieval"

#Query Data from a specific room
@app.route("/<building>/<room>/<datef>/<datet>")
def room_query(building,room,datef,datet):
    return "Successful retrival"

#Query Data from a specific building
@app.route("/<building>/<datef>/<datet>")
def building_query(building,datef,datet):
    return "Successful retrival"

#Query Sensor Data for the current day
@app.route("/<sensor>/")
def getDayData(sensor):
    return "Successful retrieval"


#Add Data to DB
@app.route("/<sensor>/<dtype>/<building>/<room>/<value>/<day>/<month>/<year>")
def addData(sensor,dtype,building, room, value,day,month,year):
    return "Successful Addition"

