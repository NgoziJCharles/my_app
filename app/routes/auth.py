#login/logout endpoints

from flask import Blueprint, render_template
from flask import request, redirect, url_for, flash, session #import flash helpers | basic tools to process a login
#request: reads from field (request.form["username"])
#redirect+url: send user to another page after login
#flash: stores one-time message (ex: wrong message)
#session: remember logged-in user id
from werkzeug.security import check_password_hash #password checker
from werkzeug.security import generate_password_hash
from app.db import get_session #openscloses DB transaction
from app.models import User, Customer #ORM model for users table | lets us query User rows (find by username)
#importing customer creates matching profile row (n/p/a) linked to new User

# '@' = decorator that tells Flash, "run next ftn when someone goes to this path"
bp = Blueprint("auth", __name__, url_prefix="/auth")
#create a blueprint obj named "auth" | routes attached to bp will live under /auth/...
@bp.get("/login") #basically tels flask to run next ftn when someone visits /auth/login
#login form page
def login_get(): return render_template("login.html")
#view ftn | shows HTML 
@bp.get("/register") #login page now has "create account" link
def register_get():
    return render_template("register.html") #load templates/register.html, send back to user
@bp.post("/register") #tells Flask to run register_post() when browser submits sign-up form to auth/register using POST
def register_post(): #start of create acc POST route
    first = request.form["first_name"].strip()
    last = request.form["last_name"].strip()
    #safely reads first and last name, strips white space, raises error if field isn't present in submitted form
    phone = request.form["phone"].strip()
    address = request.form["address"].strip()
    username = request.form["username"].strip()
    password = request.form["password"]
    if not first or not last or not phone or not address or not username or not password:
        flash("Please fill all required fields (*)", "error")
        return redirect(url_for("auth.register_get"))
    with get_session() as s:
        if s.query(User).filter_by(username=username).first(): #runs query on User table WHERE username = username | .first() = get first match
            flash("That username is taken. Choose another one please.", "error")
            return redirect(url_for("auth.register_get"))
        user = User(username=username, password_hash=generate_password_hash(password), role="user")
        #User: builds new row for users table
        s.add(user) #registers w/ current DB session so it will be written to DB when the with block commits
        s.flush() #sends pending insert to DB without closing transaction, user.id is populated immediately
        cust = Customer(name=f"{first} {last}", phone=phone, address=address, user_id=user.id)
        s.add(cust)
    flash("Account created! Please sign in.", "ok")
    return redirect(url_for("auth.login_get"))
    
@bp.post("/login") #runs next ftn when login form submitted
def login_post(): #starts view ftn
    username = request.form.get("username", "").strip() #reads username field from form
    password = request.form.get("password", "") #reads password field
    with get_session() as s: 
        user = s.query(User).filter_by(username=username).first() #looks up the User row by username
        #builts SQL query, returns first match or none
        if not user: #if username was not found
            flash("Invalid username or password", "error"); return redirect(url_for("auth.login_get"))
            #show one-time error message, send user back to login page
            #redirect...: navigates to the GET login route
        if not check_password_hash(user.password_hash, password): #compares plain password on form to hashed password in DB
            flash("Invalid username or password", "error")
            return redirect(url_for("auth.login_get"))
        session["user_id"] = user.id #records user is logged ins
        session["username"] = user.username
        session["role"] = user.role
        return redirect(url_for("dash.dashboard_home"))

@bp.get("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login_get"))
