from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()
bcrypt = Bcrypt()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    committee = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(10), default='member') # 'admin' or 'member'
    submissions = db.relationship('Submission', backref='author', lazy=True)
    evaluations = db.relationship('Evaluation', backref='member', lazy=True)

class Settings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    total_meetings = db.Column(db.Integer, default=1)
    total_events = db.Column(db.Integer, default=1)
    total_tasks = db.Column(db.Integer, default=1)
    technical_max = db.Column(db.Integer, default=55)

class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    type = db.Column(db.String(10), nullable=False) # 'meeting', 'event', 'task'
    status = db.Column(db.String(10), default='pending') # 'pending', 'approved', 'rejected'
    screenshot = db.Column(db.String(255), nullable=True)
    comment = db.Column(db.Text, nullable=True)
    title = db.Column(db.String(100), nullable=True)
    custom_date = db.Column(db.String(50), nullable=True) # "20/12/2024" etc
    date = db.Column(db.DateTime, default=datetime.utcnow)

class Evaluation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Manual Scores
    interaction_group = db.Column(db.Float, default=0.0) # max 5
    interaction_follower = db.Column(db.Float, default=0.0) # max 5
    behavior = db.Column(db.Float, default=0.0) # max 10
    hierarchy = db.Column(db.Float, default=0.0) # max 10
    bonus_head = db.Column(db.Float, default=0.0) # part of max 10
    bonus_event = db.Column(db.Float, default=0.0) # part of max 10
    technical_score = db.Column(db.Float, default=0.0) # max 55
    
    # Calculated / Stored totals
    hr_score = db.Column(db.Float, default=0.0) # max 110
    total_score = db.Column(db.Float, default=0.0) # Weighted total max 110
    grade = db.Column(db.String(2), default='-')
    published = db.Column(db.Boolean, default=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
