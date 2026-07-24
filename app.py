from flask import Flask, render_template, request,redirect,session
from models import db, User, Trek, Booking
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash,generate_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trekking.db'
app.config['SECRET_KEY']="linkingkeyforensuringsessionstates"
db.init_app(app)

with app.app_context():
    db.create_all()

@app.route("/")
def landingpage():
    return render_template("landingpage.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user_id']=user.id
            if user.role == "admin":
                return redirect("/admindashboard")
            elif user.role == "staff":
                return redirect("/staffdashboard")
            else:
                return redirect("/userdashboard")
        else:
            return "Invalid email or password"
    return render_template("login.html")

@app.route("/register",methods=["GET","POST"])
def register():
    if(request.method=="POST"):
        name=request.form['name']
        email=request.form['email']
        password=request.form['password']
        confirmpassword=request.form['confirmpassword']
        role=request.form['role']
        if(confirmpassword!=password):
            return "Passwords do not match, please re enter the same password."
        existingemail=User.query.filter_by(email=email).first()
        if(existingemail):
            return ("An account has already been regsitered with this email.")
        hashedpassword=generate_password_hash(password)
        newuser=User(name=name,role=role,password=hashedpassword,email=email)
        db.session.add(newuser)
        db.session.commit()
        return redirect("/login")
    return render_template("register.html")

@app.route("/admindashboard")
def admindashboard():
    if not session.get('user_id'):
        return redirect("/login")
    trekcount=Trek.query.count()
    staffcount=User.query.filter_by(role='staff').count()
    usercount=User.query.filter_by(role='user').count()
    bookingscount=Booking.query.count()
    recentbookings=Booking.query.order_by(Booking.id.desc()).limit(5).all()
    return render_template("admindashboard.html",trekcount=trekcount,staffcount=staffcount,usercount=usercount,bookingscount=bookingscount,recentbookings=recentbookings)


@app.route("/adminmanagetreks")
def managetreks():
    if not session.get('user_id'):
        return redirect("/login")
    treks=Trek.query.all()
    return render_template("adminmanagetreks.html",treks=treks)

@app.route("/adminmanagestaff")
def managestaff():
    if not session.get('user_id'):
        return redirect("/login")
    stafflist=User.query.filter_by(role='Staff').all()
    return render_template("adminmanagestaff.html",s=stafflist)

@app.route("/edittrek",methods=["GET","POST"])
@app.route("/addedittrek/<int:trek_id>", methods=["GET", "POST"])
def addedittrack(trek_id=None):
    if not session.get('user_id'):
        return redirect("/login")
    if(trek_id):
        toupdatetrek=Trek.query.get(trek_id)
        #take the actual trek which exists and then check for updates
    if(request.method=="POST"):
        newname=request.form.get('name_new')
        newlocation=request.form.get('location_new')
        newdifficulty=request.form.get('difficulty_new')
        newduration=request.form.get('days_new')
        newslots=request.form.get('slots_new')
        newstartdate=request.form.get('start_date_new')
        newenddate=request.form.get('end_date_new')
        newstaffname=request.form.get('staffname_new')
        newstatus=request.form.get('status_new')
        newdescription=request.form.get('description_new')

        if(trek_id):
            toupdatetrek.name=newname
            toupdatetrek.location=newlocation
            toupdatetrek.difficulty=newdifficulty
            toupdatetrek.duration=newduration
            # if(toupdatetrek.totalslots-toupdatetrek.availableslots<newslots):
            #     return "Please provide an adequate number of slots."
            # else:
            toupdatetrek.totalslots=newslots
            toupdatetrek.status=newstatus 
            toupdatetrek.assigned_staff_name=newstaffname
            toupdatetrek.start_date=newstartdate
            toupdatetrek.end_date=newenddate
            toupdatetrek.description=newdescription
            #toupdatetrek.staff_id=newstaffname 
            #this is for now
        else:
            toupdatetrek=Trek(name=newname,location=newlocation,difficulty=newdifficulty,duration=newduration,totalslots=newslots,start_date=newstartdate,end_date=newenddate,description=newdescription,assigned_staff_id=newstaffname)
            db.session.add(toupdatetrek)
        db.session.commit()
        return("added user!")

    return render_template("addedittrack.html")#, trek=toupdatetrek)

@app.route("/staffdashboard")
def staffdashboard():
    currstaff=session.get('user_id')
    if(not currstaff):
        return redirect("/login")
    assignedtreks=Trek.query.filter_by(assigned_staff_id=currstaff).all()
    treksnum=Trek.query.filter_by(assigned_staff_id=currstaff).count()
    tasksnum=Trek.query.filter_by(assigned_staff_id=currstaff,treksnum=treksnum,status='Open').count()
    participants=0
    for i in assignedtreks:
        i.participantsnum = Booking.query.filter_by(trek_id=i.id).count()
        participants+=Booking.query.filter_by(trek_id=i.id)
    
    return render_template("staffdashboard.html",assignedtreks=assignedtreks,p=participants,treksavail=tasksnum)

@app.route("/staffmanagetreks")
def staffmanagetreks():
    if not session.get('user_id'):
        return redirect("/login")
    return render_template("staffmanagetreks.html")

@app.route("/userdashboard")
def userdashboard():
    curruserid = session.get('user_id')
    if(not curruserid):
        return redirect("/login")
    curruser=User.query.get(curruserid)
    treks=Trek.query.all()
    bookings=Booking.query.filter_by(user_id=curruserid).all()
    return render_template("userdashboard.html",curruser=curruser,treks=treks,bookings=bookings)

@app.route("/usermybookings")
def usermybookings():
    if not session.get('user_id'):
        return redirect("/login")   
    return render_template("usermybookings.html")

@app.route("/usertrekkinghistory")
def usertrekkinghistory():
    if not session.get('user_id'):
        return redirect("/login")
    return render_template("usertrekkinghistory.html")

@app.route("/trekdetails/<int:id>")
def viewtrek(id):
    if not session.get('user_id'):
        return redirect("/login")
    trek=Trek.query.get(id)
    return render_template("viewtrek.html")

@app.route("/adminmanagestaff/approve/<int:staff_id>")
def approve(staff_id):
    if not session.get('user_id'):
        return redirect("/login")
    staff=User.query.get(staff_id)
    staff.status='Approved'
    db.session.commit()
    return redirect('/adminmanagestaff')

@app.route("/adminmanagestaff/reject/<int:staff_id>")
def reject(staff_id):
    if not session.get('user_id'):
        return redirect("/login")
    staff=User.query.get(staff_id)
    staff.status='Rejected'
    db.session.commit()
    return redirect('/adminmanagestaff')

if(__name__=="__main__"):
    app.debug=True
    app.run()
