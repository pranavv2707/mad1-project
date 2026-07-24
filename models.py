
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(50),nullable=False)
    email=db.Column(db.String(50),nullable=False,unique=True)
    password=db.Column(db.String(50),nullable=False)
    role=db.Column(db.String(20),nullable=False)
    contact=db.Column(db.String(20),unique=True)
    status = db.Column(db.String(20),default='Pending')

class Trek(db.Model):
    #name,location,difficulty,location,booking status,duration,total slots,available slots, start and endd dates, deacrption,staff
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50),nullable=False)
    location = db.Column(db.String(50))
    difficulty = db.Column(db.String(50),default='easy')
    duration=db.Column(db.Integer)
    totalslots=db.Column(db.Integer)
    availableslots=db.Column(db.Integer)
    status = db.Column(db.String(20), default='Pending')  
    start_date = db.Column(db.String(20))
    end_date = db.Column(db.String(20))
    description = db.Column(db.Text)
    assigned_staff_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Booking(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    trek_id = db.Column(db.Integer, db.ForeignKey('trek.id'), nullable=False)
    booking_date = db.Column(db.String(20))
    status = db.Column(db.String(20), default='Booked')



