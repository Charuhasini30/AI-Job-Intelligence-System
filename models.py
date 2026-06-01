"""Database models for the AI Job Matcher application."""
import os
from datetime import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

class User(db.Model):
    """User model to store basic user information."""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Email notification preferences
    email_notifications = db.Column(db.Boolean, default=True)
    notification_threshold = db.Column(db.Integer, default=70)  # Minimum match % for notifications
    subscribed_at = db.Column(db.DateTime)
    last_notification_sent = db.Column(db.DateTime)
    
    # Relationships
    resumes = db.relationship('Resume', backref='user', lazy=True, cascade='all, delete-orphan')
    job_applications = db.relationship('JobApplication', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.email}>'

class Resume(db.Model):
    """Resume model to store uploaded resume information and extracted skills."""
    __tablename__ = 'resumes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    file_type = db.Column(db.String(10), nullable=False)  # pdf, docx
    extracted_text = db.Column(db.Text)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed_at = db.Column(db.DateTime)
    
    # Enhanced content analysis
    experience_years = db.Column(db.Integer)
    education_level = db.Column(db.String(100))
    certifications = db.Column(db.Text)  # JSON string of certifications
    projects_count = db.Column(db.Integer, default=0)
    skills_confidence = db.Column(db.Float, default=0.0)  # Overall skill extraction confidence
    
    # Relationships
    skills = db.relationship('ExtractedSkill', backref='resume', lazy=True, cascade='all, delete-orphan')
    job_applications = db.relationship('JobApplication', backref='resume', lazy=True)
    
    def __repr__(self):
        return f'<Resume {self.original_filename}>'

class ExtractedSkill(db.Model):
    """Model to store skills extracted from resumes."""
    __tablename__ = 'extracted_skills'
    
    id = db.Column(db.Integer, primary_key=True)
    resume_id = db.Column(db.Integer, db.ForeignKey('resumes.id'), nullable=False)
    skill_name = db.Column(db.String(100), nullable=False)
    confidence_score = db.Column(db.Float, default=1.0)  # Confidence in skill extraction
    extraction_method = db.Column(db.String(50), default='keyword')  # keyword, context, semantic
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ExtractedSkill {self.skill_name}>'

class Job(db.Model):
    """Model to store job postings."""
    __tablename__ = 'jobs'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    company = db.Column(db.String(200), nullable=False)
    location = db.Column(db.String(200))
    experience_level = db.Column(db.String(100))
    description = db.Column(db.Text)
    salary_min = db.Column(db.Integer)
    salary_max = db.Column(db.Integer)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    required_skills = db.relationship('JobSkill', backref='job', lazy=True, cascade='all, delete-orphan')
    applications = db.relationship('JobApplication', backref='job', lazy=True)
    
    def __repr__(self):
        return f'<Job {self.title} at {self.company}>'

class JobSkill(db.Model):
    """Model to store required skills for jobs."""
    __tablename__ = 'job_skills'
    
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=False)
    skill_name = db.Column(db.String(100), nullable=False)
    is_required = db.Column(db.Boolean, default=True)  # Required vs Nice-to-have
    importance_level = db.Column(db.Integer, default=5)  # 1-10 scale
    
    def __repr__(self):
        return f'<JobSkill {self.skill_name} for Job {self.job_id}>'

class JobApplication(db.Model):
    """Model to track job applications and matches."""
    __tablename__ = 'job_applications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    resume_id = db.Column(db.Integer, db.ForeignKey('resumes.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=False)
    match_score = db.Column(db.Float, nullable=False)
    keyword_score = db.Column(db.Float)
    semantic_score = db.Column(db.Float)
    missing_skills_count = db.Column(db.Integer, default=0)
    status = db.Column(db.String(50), default='matched')  # matched, applied, interview, offer, rejected
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<JobApplication User:{self.user_id} Job:{self.job_id} Score:{self.match_score}>'

class SkillTrend(db.Model):
    """Model to track skill trends and popularity."""
    __tablename__ = 'skill_trends'
    
    id = db.Column(db.Integer, primary_key=True)
    skill_name = db.Column(db.String(100), unique=True, nullable=False)
    total_mentions = db.Column(db.Integer, default=0)
    job_postings_count = db.Column(db.Integer, default=0)
    resumes_count = db.Column(db.Integer, default=0)
    trend_score = db.Column(db.Float, default=0.0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<SkillTrend {self.skill_name}: {self.trend_score}>'

def init_app(app):
    """Initialize the database with the Flask app."""
    db.init_app(app)
    
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Initialize with demo jobs if none exist
        if Job.query.count() == 0:
            from dummy_jobs import get_dummy_jobs
            dummy_jobs = get_dummy_jobs()
            
            for job_data in dummy_jobs:
                job = Job(
                    title=job_data['title'],
                    company=job_data['company'],
                    location=job_data.get('location', ''),
                    experience_level=job_data.get('experience_level', ''),
                    description=job_data.get('description', '')
                )
                db.session.add(job)
                db.session.flush()  # Get the job ID
                
                # Add job skills
                for skill_name in job_data.get('required_skills', []):
                    job_skill = JobSkill(
                        job_id=job.id,
                        skill_name=skill_name,
                        is_required=True,
                        importance_level=5
                    )
                    db.session.add(job_skill)
            
            db.session.commit()
            print(f"Initialized database with {len(dummy_jobs)} jobs")