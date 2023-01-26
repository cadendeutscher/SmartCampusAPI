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


@app.before_first_request
def create_table():
    db.create_all()

#HomeRoute For Application
@app.route("/")
def hello_world():
    return "Starter Text"