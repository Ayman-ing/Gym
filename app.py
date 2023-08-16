import os
# pylint: disable=E0611

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from flask import redirect, render_template, session
from functools import wraps
from flask_moment import Moment
import datetime
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

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")
@app.route("/members", methods=["GET", "POST"])
def members():
    moment = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    #getting necessary informations 
    clients=db.execute("select cl_id,cl_Fname,cl_Lname,cl_num,cl_BD,student from client;")
    sport=db.execute("select sp_name from sport;")
    membership=db.execute("select m_id,cl_id,sp_id,ends_at from membership;")
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        #checking the validty of the phone number
        if (not request.form.get("cl_num").isnumeric()) or len(request.form.get("cl_num"))<8:
            return render_template('members.html', message1="phone number invalid",clients=clients,sport=sport,membership=membership,moment=moment)
        #checking the phone number already exist
        number=db.execute("select cl_Fname from client where cl_num=?;",request.form.get("cl_num"))
        if len(number)>0:
            return render_template('members.html', message3="phone number already exist",clients=clients,sport=sport,membership=membership,moment=moment)
        #adding the member to the table
        db.execute(
                "insert into client (cl_Fname,cl_Lname,cl_num,cl_BD,student) values(?,?,?,?,?)",
                request.form.get("cl_Fname"),
                request.form.get("cl_Lname"),
                int(request.form.get("cl_num")),
                request.form.get("cl_BD"),
                request.form.get("student") 

            )
        clients=db.execute("select cl_Fname,cl_Lname,cl_num,cl_BD,student from client;")

        if (not request.form.get("sp_name")) and (not request.form.get("m_type"))  and  (not request.form.get("duration")) and (not request.form.get("price")) and (not request.form.get("starts_at")):    
            return render_template('members.html',message2="member added successfuly",clients=clients,sport=sport,membership=membership,moment=moment)
        if (not request.form.get("sp_name")) or (not request.form.get("m_type"))  or  (not request.form.get("duration")) or (not request.form.get("price")) or (not request.form.get("starts_at")):
            return render_template('members.html',message6="member added successfuly ",message4="No membership added ! Not enough informations",clients=clients,sport=sport,membership=membership,moment=moment)
        cl_id=db.execute("select cl_id from client where cl_num=?",int(request.form.get("cl_num")))
        sp_id=db.execute("select sp_id from sport where sp_name=?",request.form.get("sp_name"))
        db.execute(
                "insert into membership (cl_id,sp_id,m_type,duration,price,starts_at,ends_at,m_status,benefits) values(?,?,?,?,?,?,date(?,'+' || ? || ' months'),?,?)",
                cl_id[0]["cl_id"],
                sp_id[0]["sp_id"],
                request.form.get("m_type"),
                int(request.form.get("duration")),
                int(request.form.get("price")),
                request.form.get("starts_at"),
                request.form.get("starts_at"),
                int(request.form.get("duration")),
                'NULL','NULL'
                )
        return render_template('members.html',message5="member and his membership added successfuly",clients=clients,sport=sport,membership=membership,moment=moment)
        
        
    else:
            
        return render_template('members.html',clients=clients,sport=sport,membership=membership,moment=moment)