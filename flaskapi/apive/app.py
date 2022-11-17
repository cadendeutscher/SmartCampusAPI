from flask import Flask, abort, request, redirect, render_template, request, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

app = Flask(__name__)
 
db = SQLAlchemy()

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Models 
#Source of help: https://flask-sqlalchemy.palletsprojects.com/en/2.x/models/
#This is a one to many relational DB Sensors are linked to their children data
class Sensor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sname = db.Column(db.String(80), nullable=False, unique=True)
    building = db.Column(db.String(80), nullable = False)
    room = db.Column(db.Integer, nullable = False)
    datas = db.relationship('SensorData', backref='sensor', lazy=True)


class SensorData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vtype = db.Column(db.String(80), nullable = False)
    value =db.Column(db.String(80), nullable = False)
    date = db.Column(db.String(80), nullable = False)
    sensor_id = db.Column(db.Integer, db.ForeignKey('sensor.id'), nullable = False)
   

#Allowed IP address for input...This are mocked IPs right now!
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

@app.before_first_request
def create_table():
    db.create_all()

#HomeRoute For Application
@app.route("/")
def hello_world():
    return render_template("main_page.html")

#Sign-in for admin    
@app.route("/signin", methods = ['POST', 'GET'])
def sign_in():
    return render_template("signin.html")

#Query Sensor Data Return JSON for specific time line
@app.route("/<sensor>/<datef>/<datet>")
def getSpecificData(sensor,datef,datet):
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

    #Query Data for todays data
    tday = datetime.now().strftime("20%y-%m-%d")
    SensorData.query.filter((SensorData.date == tday)).all()

    #Query the sensor which the data is tied to

    return "Successful retrieval"


#Add Data to DB
@app.route("/<sensor>/<dtype>/<building>/<room>/<value>/<date>")
def addData(sensor,dtype,building, room, value,date):
    #Create sensor and data objects and commit them to the DB
    asensor = Sensor(sname=sensor,building=building,room=room)
    sensordata = SensorData(vtype=dtype,value=value,date=date, sensor=asensor)
    db.session.add(asensor)
    db.session.add(sensordata)
    db.session.commit()
    return "Successful Addition"

