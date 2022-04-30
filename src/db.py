from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import *
from datetime import datetime
import hashlib
import os
import bcrypt

db = SQLAlchemy()




class User(db.Model): 
    """"
    User model: has a one-to-many relationship with Task and a one-to-many reltionship with Event
    """
    __tablename__ = "users" 
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    events = db.relationship("Event", cascade="delete") 
    tasks = db.relationship("Task", cascade="delete") 
    
    # User information
    username = db.Column(db.String, nullable=False)
    password_digest = db.Column(db.String, nullable=False)
    # Session information
    session_token = db.Column(db.String, nullable=False, unique=True)
    session_expiration = db.Column(db.DateTime, nullable=False)
    update_token = db.Column(db.String, nullable=False, unique=True)


def __init__(self, **kwargs): 
    """
    Initialize User object
    """
    self.username = kwargs.get("username")
    self.password_digest = bcrypt.hashpw(kwargs.get("password").encode("utf8"), bcrypt.gensalt(rounds=13))
    self.renew_session()


def serialize(self): 
    """
    Convert User object to dictionary
    """ 
    return {
        "id": self.id,
        "events": [e.serialize() for e in self.events],
        "tasks": [t.serialize() for t in self.tasks]
    }

# Used to randomly generate session/update tokens
def _urlsafe_base_64(self):
    return hashlib.sha1(os.urandom(64)).hexdigest()

# Generates new tokens, and resets expiration time
def renew_session(self):
    self.session_token = self._urlsafe_base_64()
    self.session_expiration = datetime.datetime.now() + datetime.timedelta(days=1)
    self.update_token = self._urlsafe_base_64()

def verify_password(self, password):
    return bcrypt.checkpw(password.encode("utf8"), self.password_digest)

# Checks if session token is valid and hasn't expired
def verify_session_token(self, session_token):
    return session_token == self.session_token and datetime.datetime.now() < self.session_expiration

def verify_update_token(self, update_token):
    return update_token == self.update_token


class Task(db.Model):
    """
    Task model: has a many-to-one relationship with User
    """
    __tablename__ = "tasks"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    task_name = db.Column(db.String, nullable=False)
    due_date = db.Column(db.String, nullable=False)
    completed = db.Column(db.Boolean, nullable=False)
    priority = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    def __init(self, **kwargs): 
        """
        Initialize Task object
        """
        self.task_name = kwargs.get("task_name")
        self.due_date = kwargs.get("due_date")
        self.completed = kwargs.get("completed")
        self.priority = kwargs.get("priority")
        self.user_id = kwargs.get("user_id")
    
    def serialize(self):
        """
        Convert Task object to dictionary
        """
        return {
            "id": self.id,
            "task_name": self.task_name,
            "due_date": self.due_date,
            "completed": self.completed,
            "priority": self.priority,
        }

class Event(db.Model):
    """
    Event model: has a many-to-one relationship with User
    """
    __tablename__ = "events"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    event_name = db.Column(db.String, nullable=False)
    description = db.Column(db.String)
    start_time = db.Column(db.String, nullable=False)
    end_time = db.Column(db.String, nullable=False)
    color = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    def __init(self, **kwargs): 
        """
        Initialize Task object
        """
        self.event_name = kwargs.get("event_name")
        self.description("description", "")
        self.start_time = kwargs.get("start_time")
        self.end_time = kwargs.get("end_time")
        self.color = kwargs.get("color", "")
        self.user_id = kwargs.get("user_id")

    def serialize(self):
        """
        Convert Event object to dictionary
        """
        return {
            "id": self.id,
            "event_name": self.event_name,
            "description": self.description,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "color": self.color,
            "user_id": self.user_id
        }







