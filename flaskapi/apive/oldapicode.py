from flask import Flask, abort, redirect, render_template, request, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
import datetime as dt
import pip._vendor.requests 

app = Flask(__name__)
 
db = SQLAlchemy()

app.secret_key = 'thisisasecretkeythatshouldbechanged'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Models 
#Source of help: https://flask-sqlalchemy.palletsprojects.com/en/2.x/models/
#More Help Here: https://www.digitalocean.com/community/tutorials/how-to-use-one-to-many-database-relationships-with-flask-sqlalchemy#step-4-displaying-a-single-post-and-its-comments
#This is a one to many relational DB Sensors are linked to their children data
class Building(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    building = db.Column(db.String(80), nullable = False)
    datas = db.relationship('Room', backref='building', lazy=True)

class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room = db.Column(db.Integer, nullable = False)
    datas = db.relationship('Sensor', backref='building', lazy=True)
    building_id = db.Column(db.Integer, db.ForeignKey('building.id'), nullable = False)

class Sensor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sname = db.Column(db.String(80), nullable=False, unique=True)
    vtype = db.Column(db.String(80), nullable = False)
    datas = db.relationship('SensorData', backref='sensor', lazy=True)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable = False)


class SensorData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value =db.Column(db.String(80), nullable = False)
    date = db.Column(db.String(80), nullable = False)
    time = db.Column(db.Integer, nullable = False)
    sensor_id = db.Column(db.Integer, db.ForeignKey('sensor.id'), nullable = False)
   

#Allowed IP address for input...These are mocked IPs right now!
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
    return render_template("main_page.html", sensors=Sensor.query.all())

#Sign-in for admin    
@app.route("/signin", methods = ['POST', 'GET'])
def sign_in():
    return render_template("signin.html")

#Query Sensor Data Return JSON for specific time line
@app.route("/sensor/<sensor>/<datef>/<datet>")
def getSpecificData(sensor,datef,datet):
    #Query Data for a sensor
    sData = Sensor.query.filter((Sensor.sname == sensor)).one()
    #create date object for from date
    fyear = int(datef[0:4])
    fmonth = int(datef[5:7])
    fday = int(datef[8:10])
    fdate = dt.date(fyear,fmonth,fday)
     #create date object from todate
    tyear = int(datet[0:4])
    tmonth = int(datet[5:7])
    tday = int(datet[8:10])
    tdate = dt.date(tyear,tmonth,tday)
    dList = []
    sensorData = sData.datas
    #sort through the different data objects
    for data in sensorData:
        #create a date object for the data from the sensor
        dyear = int(data.date[0:4])
        dmonth =int(data.date[5:7])
        dday = int(data.date[8:10])
        currentD = dt.date(dyear,dmonth,dday)
        #check if the sensor date is between the from and todates 
        if fdate <= currentD and tdate >= currentD:
            dDic = {
            "sid": data.id,
            "sensor": sData.sname,
            "vtype": sData.vtype,
            "building": sData.building,
            "room": sData.room,
            "did": data.id,
            "time": data.time,
            "value": data.value,
            "date": data.date
            }
            dList.append(dDic)
    return json.dumps(dList)

   
#Query Data from a specific room
@app.route("/<building>/<room>/<datef>/<datet>")
def room_query(building,room,datef,datet):
    #Query Data for todays sensors
    sData = Sensor.query.filter((Sensor.room == room)).all()
   
    #create date object for from date
    fyear = int(datef[0:4])
    fmonth = int(datef[5:7])
    fday = int(datef[8:10])
    fdate = dt.date(fyear,fmonth,fday)
     #create date object from todate
    tyear = int(datet[0:4])
    tmonth = int(datet[5:7])
    tday = int(datet[8:10])
    tdate = dt.date(tyear,tmonth,tday)
    dList = []
    #if the data is for today create a JSON object add it to a JSONArray and return the array
    #sort through the sensors
    for sensors in sData:
        sensorData = sensors.datas
        #sort through the different data objects
        for data in sensorData:
            #create a date object for the data from the sensor
            dyear = int(data.date[0:4])
            dmonth =int(data.date[5:7])
            dday = int(data.date[8:10])
            currentD = dt.date(dyear,dmonth,dday)
            #check if the sensor date is between the from and to dates 
            if fdate <= currentD and tdate >= currentD:
                dDic = {
                "sid": sensors.id,
                "sensor": sensors.sname,
                "vtype": sensors.vtype,
                "building": sensors.building,
                "room": sensors.room,
                "did": data.id,
                "value": data.value,
                "date": data.date,
                "time": data.time

                }
                dList.append(dDic)
    return json.dumps(dList)

   
#Query Data from a specific building
@app.route("/building/<building>/<datef>/<datet>")
def building_query(building,datef,datet):
    #Query Data for todays sensor
    sData = Sensor.query.filter((Sensor.building == building)).all()
   
    #create date object for from date
    fyear = int(datef[0:4])
    fmonth = int(datef[5:7])
    fday = int(datef[8:10])
    fdate = dt.date(fyear,fmonth,fday)
     #create date object from todate
    tyear = int(datet[0:4])
    tmonth = int(datet[5:7])
    tday = int(datet[8:10])
    tdate = dt.date(tyear,tmonth,tday)
    dList = []
    #if the data is for today create a JSON object add it to a JSONArray and return the array
    #sort through the sensors
    for sensors in sData:
        sensorData = sensors.datas
        #sort through the different data objects
        for data in sensorData:
            #create a date object for the data from the sensor
            dyear = int(data.date[0:4])
            dmonth =int(data.date[5:7])
            dday = int(data.date[8:10])
            currentD = dt.date(dyear,dmonth,dday)
            #check if the sensor date is between the from and todates 
            if fdate <= currentD and tdate >= currentD:
                dDic = {
                "sid": sensors.id,
                "sensor": sensors.sname,
                "building": sensors.building,
                "vtype": sensors.vtype,
                "room": sensors.room,
                "did": data.id,
                "value": data.value,
                "date": data.date,
                "time": data.time
                }
                dList.append(dDic)
    return json.dumps(dList)


#Query Sensor Data for the current day
@app.route("/<sensor>/")
def getDayData(sensor):
    #Query Data for todays sensor
    sData = Sensor.query.filter((Sensor.sname == sensor)).one()
    sensorData = sData.datas
    #Get current date
    tday = datetime.now().strftime("20%y-%m-%d")
    dList = [{"senorID": sData.id, "sensorName" : sData.sname, "building" : sData.building, "room" : sData.room, "vtype": sData.vtype, "data" : []}]
    #if the data is for today create a JSON object add it to a JSONArray and return the array
    for data in sensorData:
        if data.date == tday:
            dDic = {
            "did": data.id,
            "value": data.value,
            "date": data.date,
            "time": data.time
            }
            dList[0]["data"].append(dDic)

    next_url = request.args.get('next')
    #if this url was accessed directly pass back a JSON Array other wise go back to the original route
    if next_url is None:
        return json.dumps(dList)
    else:
        return redirect(url_for('displaySensorInfo', sensorName=sensor, data=json.dumps(dList)))
 

#Add Data to DB
#/t/kwh/shiley/201/15/2023-01-12/1815
@app.route("/<sensor>/<dtype>/<building>/<room>/<value>/<date>/<time>")
def addData(sensor,dtype,building, room, value, date, time):
    #Check if sensor already exsists in database
    theSensor = Sensor.query.filter((Sensor.sname == sensor)).first()
    #if the sensor does not exsist create it, otherwise just add the data.
    if theSensor is None:
        #Create sensor and data objects and commit them to the DB
        #Create Sensor
        asensor = Sensor(sname=sensor,building=building,room=room, vtype=dtype)
        db.session.add(asensor)
    else: 
        #make set the sensor to add the data to, to be equal to the queried sensor
        asensor = theSensor

    #Create Sensor Data assigned to sensor
    sensordata = SensorData(value=value,date=date, time=time, sensor=asensor)
    db.session.add(sensordata)
    #Commit Data to database
    db.session.commit()
    return "Successful Addition"

# Display the charts and graphs for a specific sensor
@app.route("/info/<sensorName>")
def displaySensorInfo(sensorName):
    data = request.args.get('data')
    #Check if the data has already been queried 
    if data is None:
        #Redirect to the getDayData url to get JSON objects for the days date...by passing the next arguement we tell it to redirect back here
        return redirect(url_for('getDayData', sensor = sensorName, next="redirect"))
    else:
        #Load the data as a JSON dictionary if it exists
        data = json.loads(data)
        return render_template("sensorinfo.html", data=data)
