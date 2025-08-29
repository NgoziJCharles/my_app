#4 tables as ORM (object-relational mapper: connects Python objs to DB tables) classes
from sqlalchemy.orm import declarative_base, relationship #ORM helpers
#dec_base: gives base class; relationship: lets models link
#how classes map to tables and how I navigate joins in Python
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy import DateTime, CheckConstraint, func, Index

Base = declarative_base() #creates parent class for all models
#foundation of ORM pattern

class User(Base): #represents a table
    __tablename__ = "users" #exact table name in DB
    #creates a table called users
    id = Column(Integer, primary_key=True) #col named id, type Int, marked as primary key
    #uniquely id's each row
    username = Column(String(50), unique=True, nullable=False) #text col up to 50 chars
    #enforces uniqye usernames
    password_hash = Column(String(255), nullable=False) #text col up to 255 chars
    #stores hashed password, can't be empty
    role = Column(String(20), nullable=False, default="user") #small text col for role (user, admin)
    #defaults to user
    customer = relationship("Customer", back_populates="user", uselist=False)
    #uselist: tells SQLAlchemy this is one row, not a list
    created_at = Column(DateTime, server_default=func.now())
    #timestamp of when row was created
    #for debugging

class Customer(Base): #Pythin class named Customer that inherits from Base
#used to store each user's profile info
    __tablename__ = "customers" #table called customers
    id = Column(Integer, primary_key=True) #adds an id col and marks it as primary key
    name = Column(String(120), nullable=False) #adds a name text col that cannot be empty
    phone = Column(String(30)) #a text col to store customer's phone nums up to 30 chars
    address = Column(String(200)) #a text col to store customer's address up to 200 chars
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False) #int col that references users.id
    #does foreign key to link users table, enforces one customer per user (unique)
    #real DB connection betwee login (User) and profile (Customer)
    user = relationship("User", back_populates="customer")
    #lets me write customer.user in Python
    #back_populates: syncs User
    projects = relationship("Project", back_populates="customer", cascade="all, delete-orphan")
    created_at = Column(DateTime, server_default=func.now())
    __table_args__ = (Index("ix_customers_name", "name"),)
    def __repr__(self): return f"<Customer id={self.id} name={self.name}>"


class Project(Base): #stores each customer's project
    __tablename__ = "projects" #names the table projects
    id = Column(Integer, primary_key=True) #unique ID for ezch project row
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, index=True)
    #links each project to one customer, index speeds up lookups by customer
    #index: DS that keeps a sorted list of valuers for a column and where to find matching rows
    name = Column(String(120), nullable=False) #stores project name up to 120 chars
    stage = Column(Integer, nullable=False) #stores project stage 1-6
    __table_args__ = (CheckConstraint("stage >= 1 AND stage <= 6", name="chk_stage_1_6"),) #makes sure stage is between 1-6
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    #timestamp col | autoupdates when row changes
    customer = relationship("Customer", back_populates="projects")
    #allows projects.customer
    histories = relationship("ProjectStageHistory", back_populates="project", cascade="all, delete-orphan")
    #list of stage-change rows | project.histories gives all changes
    #cascade: if proj is deleted, histories are deleted too

class ProjectStageHistory(Base): #defines history table | store every stage here
    __tablename__ = "project_stage_history" #name of table
    id = Column(Integer, primary_key=True) #unique ID
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    #link each history row to exactly one proj 
    old_stage = Column(Integer, nullable=False) 
    new_stage = Column(Integer, nullable=False)
    changed_at = Column(DateTime, server_default=func.now())
    project = relationship("Project", back_populates="histories")
    #allows histories.project
    __table_args__ = (Index("ix_hist_project_changed", "project_id", "changed_at"),)




