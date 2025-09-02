#shows name/phone/address/proj stage
from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from app.db import get_session
from app.models import Customer, Project
from sqlalchemy import text




bp = Blueprint("dash", __name__, url_prefix="/dashboard")
 #creates blueprint named dash
@bp.get("/")
def dashboard_home(): 
    if "user_id" not in session: return redirect(url_for("auth.login_get")) #if not logged in, send to login page
    with get_session() as s:
        cust = s.query(Customer).filter_by(user_id=session["user_id"]).first()
        #looking up on Customer row, whose user_id = logged-in user's id
        projects = [] #init empty list, gives default val if user has no customer profile
        if cust: #if customer record found
            projects = s.query(Project).filter_by(customer_id=cust.id).order_by(Project.updated_at.desc()).all()
            #pulls back list of proj objs from DB so to show user's projs on dashboard, sorted by recent activity    

    stage_labels = {1:"Stage 1", 2:"Stage 2", 3:"Stage 3", 4:"Stage 4", 5:"Stage 5", 6:"Stage 6"} #dict mapping stage numbers
    return render_template("dashboard.html", customer=cust, projects=projects, stage_labels=stage_labels)

@bp.post("/projects")
def create_project():
    if "user_id" not in session:
        return redirect(url_for("auth.login_get"))

    name = request.form.get("name", "").strip()
    stage_raw = request.form.get("stage", "").strip()
    if not name or not stage_raw:
        flash("Project name and stage are required", "error")
        return redirect(url_for("dash.dashboard_home"))

    allowed = {"1", "2", "3", "4", "5", "6"}
    if stage_raw not in allowed:
        flash("Stage must be 1–6", "error")
        return redirect(url_for("dash.dashboard_home"))
    stage = int(stage_raw)

    with get_session() as s:
        cust = s.query(Customer).filter_by(user_id=session["user_id"]).first()
        if not cust:
            flash("Profile not found. Please complete registration.", "error")
            return redirect(url_for("auth.register_get"))

        proj = Project(customer_id=cust.id, name=name, stage=stage)
        s.add(proj)
        flash("Project added", "success")

    return redirect(url_for("dash.dashboard_home"))

    