#shows name/phone/address/proj stage

from flask import Blueprint, render_template, session, redirect, url_for
from app.db import get_session
from app.models import Customer, Project

bp = Blueprint("dash", __name__, url_prefix="/dashboard") #creates blueprint named dash
@bp.get("/")
def dashboard_home(): 
    if "user_id" not in session: return redirect(url_for("auth.login_get")) #if not logged in, send to login page
    with get_session() as s:
        cust = s.query(Customer).filter_by(user_id=session["user_id"]).first()
        projects = []
        if cust:
            projects = s.query(Project).filter_by(customer_id=cust.id).order_by(Project.updated_at.desc()).all()
