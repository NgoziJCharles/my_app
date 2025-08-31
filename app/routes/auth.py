#login/logout endpoints

from flask import Blueprint, render_template
from flask import request, redirect, url_for, flash, session #import flash helpers | basic tools to process a login
#request: reads from field (request.form["username"])
#redirect+url: send user to another page after login
#flash: stores one-time message (ex: wrong message)
#session: remember logged-in user id
from werkzeug.security import check_password_hash #password checker
from app.db import get_session #openscloses DB transaction
from app.models import User #ORM model for users table | lets us query User rows (find by username)


bp = Blueprint("auth", __name__, url_prefix="/auth")
#create a blueprint obj named "auth" | routes attached to bp will live under /auth/...
@bp.get("/login") #basically tels flask to run next ftn when someone visits /auth/login
#login form page
def login_get(): return render_template("login.html")
#view ftn | shows HTML f
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
