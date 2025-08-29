#create tables and insert demo data

from app.db import engine, get_session #get_session: context-manager helper for opening/committing/etc... DB sessions
from app.models import Base, User, Customer, Project, ProjectStageHistory

Base.metadata.create_all(bind=engine) #creates every table defined on Base if it doesn't exist yet
#runs necessary create table statements
print("tables created")

from werkzeug.security import generate_password_hash
#i,ports helper that turns plain password into secure hash
with get_session() as s: #opens DB session using context manager from app/db
#starts transaction, on success = commit, on error = roll back, close
    u = User(username="demo", password_hash=generate_password_hash("secret123"), role="user")
    #builds  user obj in Python
    #creates login acc to sign in
    c = Customer(name="demo User", phone="123-456-7890", address="123 Fake", user=u)
    #build customer profile obj and link to the User via user=u
    #sets display info and wires 1:1 relationship
    s.add_all([u,c]) #tells SQLAlchemy to track these 2 new objs
    #marks u and c as pending inserts, written at commit
    p = Project(name="Demo Proj", stage=1, customer=c) #build new proj obj linked to c
    #fills name, stage; sets customer_id: customer=c
    s.add(p) #add proj to session
    print("seeded demo u/c/p") 

