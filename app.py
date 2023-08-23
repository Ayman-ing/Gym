import os
# pylint: disable=E0611

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session , url_for
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from flask import redirect, render_template, session
from functools import wraps
from flask_moment import Moment
import datetime
import calendar
def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
moment = Moment(app)
# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///gym1.db")

@app.route("/")
@login_required
def index():
    return render_template("index.html")
@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template("login.html",message1="must provide username")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("login.html",message2="must provide password")
        # Query database for username
        rows = db.execute(
            "SELECT ad_id,hash FROM Admin WHERE ad_username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return render_template("login.html",message3="username or password incorrect")

        # Remember which user has logged in
        session["user_id"] = rows[0]["ad_id"]

        # Redirect user to home page

        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # User reached route via POST (as by submitting a form via POST)

    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template("register.html", message1="must provide username")
        if not request.form.get("mail"):
            return render_template("register.html", message2="must provide your mail")
        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("register.html", message3="must provide password")
        # Ensure password confirmation was submitted
        elif not request.form.get("confirmation"):
            return render_template("register.html", message4="must provide confirmation")
        # Ensure password confirmation match the password
        elif request.form.get("confirmation") != request.form.get("password"):
            return render_template("register.html", message5="password must match confirmation")
        # query the database
        rows_username = db.execute(
            "SELECT * FROM Admin WHERE ad_username = ?", request.form.get("username")
        )
        rows_mail = db.execute("SELECT * FROM Admin WHERE ad_mail = ?", request.form.get("mail"))
        # checking the username is unique
        if len(rows_username) > 0:
            return  render_template("register.html", message6="username taken")
        #checking the mail doesn't exist
        if len(rows_mail) > 0:
            return  render_template("register.html", message7="mail already exist")
        # generating the hash password
        pwhash = generate_password_hash(request.form.get("password"))
        # adding the user
        db.execute(
            "INSERT INTO Admin (ad_username,ad_mail,hash) VALUES (?,?,?)",
            request.form.get("username"),
            request.form.get("mail"),
            pwhash

        )
        # getting the user id
        user_id = db.execute(
            "SELECT ad_id FROM Admin WHERE ad_username = ?", request.form.get("username")
        )
        # Remember which user has logged in
        session["user_id"] = user_id[0]["ad_id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")
@login_required
@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/members", methods=["GET", "POST"])
@login_required
def members():
    #the delete function
    def delete():
        #checking if it's deleting a member or a membership
        if request.form.get("form_id")=="form3cl" :
            db.execute("delete from client where cl_id=?",int(request.form.get("cl_id")))
            return render_template("members.html",message8="member deleted succssefuly",member=member,moment=moment,clients=clients,sport=sport)
        else:
            db.execute("delete from membership where cl_id=?",int(request.form.get("cl_id")))
            return render_template("members.html",message8="membership deleted succssefuly",member=member,moment=moment,clients=clients,sport=sport)

    #the edit function
    def edit():
        #the client editing function
        def edit_cl():
            if request.form.get("cl_num"):   
                #checking the phone number already exist
                num=db.execute("select cl_Fname from client where cl_num=?;",request.form.get("cl_num"))
                if len(num)>0:
                    return render_template('members.html', message3="phone number already exist",member=member,moment=moment,clients=clients,sport=sport)
                #checking the validty of the phone number
                if (not request.form.get("cl_num").isnumeric()) or len(request.form.get("cl_num"))<8:
                    return render_template('members.html', message1="phone number invalid",member=member,moment=moment,clients=clients,sport=sport)
            dict_m={"cl_Fname":request.form.get("cl_Fname"),"cl_Lname":request.form.get("cl_Lname"),"cl_BD":request.form.get("cl_BD"),
                    "cl_num":request.form.get("cl_num"),"student":request.form.get("student")}
            for key,value in dict_m.items():
                if value:
                    db.execute("UPDATE client set ?=? where cl_id=?",key,value,int(request.form.get("cl_id")))
        #the membership editing function    
        def edit_m():
            result=edit_cl()
        
            if result is None :
                dict_msh={"m_type":request.form.get("m_type"),"duration":request.form.get("duration"),"price":request.form.get("price")}
                
                #"sp_name"
                if request.form.get("sp_name"):
                    sp_id=db.execute("select sp_id from sport where sp_name=?",request.form.get("sp_name"))
                    db.execute("update membership set sp_id=? where m_id=?",sp_id[0]["sp_id"],int(request.form.get("m_id")))
                    
                if request.form.get("starts_at") or request.form.get("duration"):
                    db.execute("UPDATE membership set starts_at=? ,ends_at=date(?,'+' || ? || ' months') where m_id=?",request.form.get("starts_at"),request.form.get("starts_at"),int(request.form.get("duration")),int(request.form.get("m_id")))
                
                for key,value in dict_msh.items():
                    if value:
                        db.execute("UPDATE membership set ?=? where m_id=?",key,value,int(request.form.get("m_id")))
                return render_template("members.html",message7="changes made successfuly",member=member,moment=moment,clients=clients,sport=sport)
            else :
                return result       
        #checking whether it's editing a client or a client and membership
        if request.form.get("form_id") =="form2m":
            return edit_m()
        elif request.form.get("form_id") =="form2cl":
            result2=edit_cl()
            if result2 is None:
                return render_template("members.html",message7="changes made successfuly",member=member,moment=moment,clients=clients,sport=sport)
            else :
                return result2
    #add function
    def add():
        #adding client
        def add_cl():
            #checking the validty of the phone number
            if (not request.form.get("cl_num").isnumeric()) or len(request.form.get("cl_num"))<8:
                return render_template('members.html', message1="phone number invalid",member=member,moment=moment,clients=clients,sport=sport)
            #checking the phone number already exist
            number=db.execute("select cl_Fname from client where cl_num=?;",request.form.get("cl_num"))
            if len(number)>0:
                return render_template('members.html', message3="phone number already exist",member=member,moment=moment,clients=clients,sport=sport)
            #adding the member to the table
            db.execute(
                    "insert into client (cl_Fname,cl_Lname,cl_num,cl_BD,student) values(?,?,?,?,?)",
                    request.form.get("cl_Fname"),
                    request.form.get("cl_Lname"),
                    int(request.form.get("cl_num")),
                    request.form.get("cl_BD"),
                    request.form.get("student") 

                )
        #adding membership
        def add_m():
            
            #adding the membership
            if (not request.form.get("sp_name")) and (not request.form.get("m_type"))  and  (not request.form.get("duration")) and (not request.form.get("price")) and (not request.form.get("starts_at")):    
                return "member added successfuly"
            if (not request.form.get("sp_name")) or (not request.form.get("m_type"))  or  (not request.form.get("duration")) or (not request.form.get("price")) or (not request.form.get("starts_at")):
                return "No membership added ! Not enough informations"
            if not request.form.get("cl_id"):
                cl_id=db.execute("select cl_id from client where cl_num=?",int(request.form.get("cl_num")))
            else:
                cl_id=[{}]
                cl_id[0]["cl_id"]=int(request.form.get("cl_id"))
            sp_id=db.execute("select sp_id from sport where sp_name=?",request.form.get("sp_name"))
            db.execute(
                    "insert into membership (cl_id,sp_id,m_type,duration,price,starts_at,ends_at) values(?,?,?,?,?,?,date(?,'+' || ? || ' months'))",
                    cl_id[0]["cl_id"],
                    sp_id[0]["sp_id"],
                    request.form.get("m_type"),
                    int(request.form.get("duration")),
                    int(request.form.get("price")),
                    request.form.get("starts_at"),
                    request.form.get("starts_at"),
                    int(request.form.get("duration")),
                    
                    )
            
        #checking whether it's adding a membership only or  all full information
        if request.form.get("form_id") =="form1cl":
            result1=add_m()
            if result1 is None:

                return render_template('members.html',message5="membership added successfuly",member=member,moment=moment,clients=clients,sport=sport)
            else:
                return render_template("members.html",message3="No membership added ! Not enough informations",member=member,moment=moment,clients=clients,sport=sport)
        elif request.form.get("form_id") =="form1m": 
            result2=add_cl()
            if result2 is None :
                result3=add_m()
                if result3 is None:
                    return render_template('members.html',message5="member and his membership added successfuly",member=member,moment=moment,clients=clients,sport=sport)
                else:
                    return render_template('members.html',message5="member added successfuly",message3="No membership added ! Not enough informations",member=member,moment=moment,clients=clients,sport=sport)
            else:
                return result2
    
    
    
    moment = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    #getting necessary informations 
    sport=db.execute("select sp_name from sport;")
    member=db.execute("select * from member;")
    clients=db.execute("select cl_id,cl_Fname,cl_Lname,cl_num,cl_BD,student from client where cl_id NOT IN (SELECT cl_id from membership) ;")
    for m in member:
        if moment  >= m["ends_at"]:
            m["status"]="inactive"
        else:
            m["status"]="active"
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        
        #checking if it's an adding,edit or a delete
        if "form1" in request.form.get("form_id"):
            return add()
        elif "form2" in request.form.get("form_id") :
            return edit()
        elif "form3" in request.form.get("form_id") :
            return delete()
            
        
        
        
    #user reached route via GET    
    else:
            
        return render_template('members.html',member=member,moment=moment,clients=clients,sport=sport)
def generate_calendar(year, month):
        # Create a calendar for the specified year and month
        cal = calendar.monthcalendar(year, month)
        return cal
@app.route("/schedule/<int:year>/<int:month>", methods=["GET", "POST"])
@login_required
def schedule(year,month):
    
    if request.method =="GET":
        cal=generate_calendar(year,month)
        events=db.execute("select sp_id,starts_at,ends_at,days,start_date,end_date from schedule;")
        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        current_events={}
        for activity in events:
            activity["sp_name"]=db.execute("select sp_name from sport where sp_id=?",activity["sp_id"])
            start_month_condition=(int(activity["start_date"][0:4])==year and int(activity["start_date"][5:7])<=month)
            start_year_condtion=int(activity["start_date"][0:4])<year
            end_month_condition=(int(activity["end_date"][0:4])==year and int(activity["end_date"][5:7])>=month)
            end_year_condition=int(activity["end_date"][0:4])>year
            if (start_year_condtion or start_month_condition   )and (end_year_condition or end_month_condition ):
                days=[day for day in activity["days"].split(",") if day]
                
                for week in cal:
                    
                    for day in range(7):
                        if str(day) in days and week[day]!=0:
                            formatted_date = '{:04d}-{:02d}-{:02d}'.format(year, month,week[day])
                            current_events[formatted_date]=[activity["sp_name"][0]["sp_name"],activity["starts_at"],activity["ends_at"]]
        sport=db.execute("select sp_name from sport;")
        return render_template("schedule.html",cal=cal,start_month_condition=start_month_condition,month=month,year=year,current_events=current_events,sport=sport)
    elif request.method=="POST":
        sp_id=db.execute("select sp_id from sport where sp_name=?",request.form.get("sp_name"))
        days=""
        list=request.form.getlist("days[]")
        for day in list:
            days=days + day +","
        db.execute("insert into schedule  (sp_id,starts_at,ends_at,repeat_pattern,days,start_date,end_date) values(?,?,?,?,?,?,?)",
                    sp_id[0]["sp_id"],
                    request.form.get("starts_at"),
                    request.form.get("ends_at"),
                    request.form.get("repeat_pattern"),
                    days,
                    request.form.get("start_date"),
                    request.form.get("end_date"),
                                        )
        
        date=request.form.get("event_date")
        return render_template("index.html",year=year,month=month,date=date,days=days)

@app.route('/schedule', methods=["GET", "POST"])
@login_required
def current_month_calendar():
    if request.method =="GET":
        now = datetime.datetime.now()
        year = now.year
        month = now.month
        return redirect(url_for('schedule', year=year, month=month))
