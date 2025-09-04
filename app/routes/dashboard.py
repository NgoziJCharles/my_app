#shows name/phone/address/proj stage
from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from app.db import get_session
from app.models import Customer, Project, ProjectStageHistory, Notification
from sqlalchemy import text
from datetime import datetime





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
        last_seen_raw = session.get("notes_last_seen")
        try:
            last_seen_dt = datetime.fromisoformat(last_seen_raw) if last_seen_raw else datetime(1970,1,1)
        except Exception:
            last_seen_dt = datetime(1970,1,1)
        unread_count = s.query(Notification).filter(Notification.user_id==session["user_id"], Notification.created_at > last_seen_dt).count()
    

    avg_stage = round(sum(p.stage for p in projects) / len(projects), 2) if projects else None
    if not projects:
        status_text, status_class = "-", "status-muted"
    elif avg_stage >= 3:
        status_text, status_class = "On Track", "status-ok"
    else:
        status_text, status_class = "Not on Track", "status-bad"
    stage_labels = {1:"Stage 1", 2:"Stage 2", 3:"Stage 3", 4:"Stage 4", 5:"Stage 5", 6:"Stage 6"}
    return render_template(
    "dashboard.html",
    customer=cust, projects=projects, stage_labels=stage_labels,
    status_text=status_text, status_class=status_class, avg_stage=avg_stage, unread_count=unread_count
)

@bp.get("/notifications")
def notifications():
    if "user_id" not in session:
        return redirect(url_for("auth.login_get"))
    with get_session() as s:
        notes = (s.query(Notification)
                .filter_by(user_id=session["user_id"])
                .order_by(Notification.created_at.desc()).all())
    session["notes_last_seen"] = datetime.utcnow().isoformat()
    session.modified = True
    return render_template("notifications.html", notifications=notes, unread_count=0)


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

@bp.post("/projects/<int:project_id>/delete")
def delete_project(project_id):
    if "user_id" not in session: return redirect(url_for("auth.login_get"))
    with get_session() as s:
        proj = s.query(Project).join(Customer).filter(Project.id==project_id, Customer.user_id==session["user_id"]).first()
        if not proj:
            flash("Project not found", "error"); return redirect(url_for("dash.dashboard_home"))
        s.delete(proj)
        flash("Project deleted", "success")
    return redirect(url_for("dash.dashboard_home"))

@bp.post("/projects/<int:project_id>/edit")
def edit_project(project_id):
    if "user_id" not in session: 
        return redirect(url_for("auth.login_get"))
    name = request.form.get("name","").strip()
    stage_raw = request.form.get("stage","").strip()
    if not name or not stage_raw: 
        flash("Project name and stage are required","error"); 
        return redirect(url_for("dash.dashboard_home"))
    allowed = {"1","2","3","4","5","6"}
    if stage_raw not in allowed: flash("Stage must be 1–6","error"); return redirect(url_for("dash.dashboard_home"))
    stage = int(stage_raw)
    with get_session() as s:
        proj = s.query(Project).join(Customer).filter(Project.id==project_id, Customer.user_id==session["user_id"]).first()
        if not proj: flash("Project not found","error"); return redirect(url_for("dash.dashboard_home"))
        old_stage = proj.stage
        name_changed  = (name  != proj.name)
        stage_changed = (stage != proj.stage)
        # notify only when moving 1 -> 2
        if stage_changed:
            s.add(ProjectStageHistory(project_id=proj.id, old_stage=old_stage, new_stage=stage))
        if name != proj.name or stage != proj.stage:
            proj.name = name
            proj.stage = stage
            s.flush()
            stages = [st for (st,) in s.query(Project.stage).join(Customer).filter(Customer.user_id==session["user_id"]).all()]
            avg_stage = (sum(stages)/len(stages)) if stages else 0
            status = "on track" if avg_stage >= 3 else "not on track"
            if stage_changed and old_stage == 1 and stage == 2:
                s.add(Notification(user_id=session["user_id"], message=f"{proj.name} has changed from Stage 1 to Stage 2 — you are now {status}"))
            flash("Project updated", "success")
    return redirect(url_for("dash.dashboard_home"))

