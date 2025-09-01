#app factory | where I create the Flask app and register routes

from flask import Flask, session, redirect, url_for
import os
from dotenv import load_dotenv

load_dotenv() #execute load | reads .env

def create_app():
    app = Flask(__name__) #constructs Flask application | sets up routing, templates, etc
    from werkzeug.middleware.proxy_fix import ProxyFix
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret")
    #reads secret_key from .env, falls back to dev-secret if missing
    @app.get("/health")
    def health():
        return "ok", 200

    @app.get("/")
    def home():
        if "user_id" not in session:
            return redirect(url_for("auth.login_get"))
        return redirect(url_for("dash.dashboard_home"))


    from app.routes.auth import bp as auth_bp #imports Blueprint obj created in app/routes/auth.py
    app.register_blueprint(auth_bp) #attaches all routes from auth bllueprint

    from app.routes.dashboard import bp as dash_bp  #import the dashboard blueprint object
    app.register_blueprint(dash_bp)#attach its routes (under /dashboard/...)

    app.config["TEMPLATES_AUTO_RELOAD"] = True #flask will auto-reload templates when editting .html files
    app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0 
    
    return app
