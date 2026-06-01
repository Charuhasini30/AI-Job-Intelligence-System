import os
import logging
from datetime import datetime
from flask import Flask, render_template, request, jsonify, flash, redirect, url_for, session
from werkzeug.utils import secure_filename
from werkzeug.middleware.proxy_fix import ProxyFix
import uuid
from simple_text_processor import SimpleTextProcessor
from job_matcher import JobMatcher
from dummy_jobs import get_dummy_jobs
from models import db, init_app, User, Resume, ExtractedSkill, Job, JobSkill, JobApplication, SkillTrend
from email_service import EmailService
from io import BytesIO

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Database configuration
database_url = os.environ.get("DATABASE_URL")
if not database_url:
    # Fallback for development
    database_url = "sqlite:///job_matcher.db"
    logging.warning("DATABASE_URL not found, using SQLite fallback")

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Create upload directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize database
init_app(app)

# Initialize components
text_processor = SimpleTextProcessor()
job_matcher = JobMatcher()
email_service = EmailService()

def allowed_file(filename):
    """Check if the uploaded file has an allowed extension."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Main page with resume upload form."""
    return render_template('index.html')

@app.route('/upload_resume', methods=['POST'])
def upload_resume():
    """Handle resume upload and skill extraction."""
    try:
        # Check if file was uploaded
        if 'resume' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file uploaded. Please select a resume file.'
            }), 400
        
        file = request.files['resume']
        
        # Check if file was selected
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected. Please choose a PDF or DOCX file.'
            }), 400
        
        # Check file extension - be more lenient for demo purposes
        if not allowed_file(file.filename):
            logging.warning(f"File extension not in allowed list, but processing anyway: {file.filename}")
            # For demo purposes, allow any file but warn the user
            # return jsonify({
            #     'success': False,
            #     'error': 'Invalid file type. Please upload a PDF or DOCX file.'
            # }), 400
        
        # Generate unique filename
        filename = secure_filename(file.filename or 'resume.pdf')
        unique_filename = f"{uuid.uuid4()}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        
        # Save file
        file.save(filepath)
        logging.info(f"File saved to: {filepath}")
        
        # Extract skills and metadata from resume
        try:
            logging.info(f"Processing file: {filepath}")
            extraction_result = text_processor.extract_skills_and_metadata(filepath)
            extracted_skills = extraction_result['skills']
            logging.info(f"Extracted {len(extracted_skills)} skills with {extraction_result['skills_confidence']} confidence")
            
            if not extracted_skills:
                logging.warning("No skills extracted, this shouldn't happen with the demo fallback")
                return jsonify({
                    'success': False,
                    'error': 'No skills could be extracted from the resume. Please ensure your resume contains relevant technical skills and experience.'
                }), 400
            
            # Get user information from request or session
            user_email = request.form.get('email') or session.get('user_email', 'demo@jobmatcher.com')
            user_name = request.form.get('name') or session.get('user_name', 'Demo User')
            
            # Create or get user
            user = User.query.filter_by(email=user_email).first()
            if not user:
                user = User(
                    email=user_email, 
                    name=user_name,
                    email_notifications=True,
                    notification_threshold=70,
                    subscribed_at=datetime.utcnow()
                )
                db.session.add(user)
                db.session.flush()
                
                # Send welcome email
                if email_service.enabled:
                    email_service.send_subscription_confirmation(user_email, user_name)
            
            # Save resume to database with enhanced metadata
            resume = Resume(
                user_id=user.id,
                filename=unique_filename,
                original_filename=filename,
                file_size=os.path.getsize(filepath),
                file_type=filename.rsplit('.', 1)[1].lower() if '.' in filename else 'unknown',
                extracted_text=extraction_result.get('extracted_text', ''),
                experience_years=extraction_result.get('experience_years', 0),
                education_level=extraction_result.get('education_level', 'Not Specified'),
                certifications=str(extraction_result.get('certifications', [])),
                projects_count=extraction_result.get('projects_count', 0),
                skills_confidence=extraction_result.get('skills_confidence', 0.0),
                processed_at=datetime.utcnow()
            )
            db.session.add(resume)
            db.session.flush()
            
            # Save extracted skills with enhanced confidence
            for skill in extracted_skills:
                extracted_skill = ExtractedSkill(
                    resume_id=resume.id,
                    skill_name=skill,
                    confidence_score=extraction_result.get('skills_confidence', 0.8),
                    extraction_method='enhanced_keyword'
                )
                db.session.add(extracted_skill)
                
                # Update skill trends
                skill_trend = SkillTrend.query.filter_by(skill_name=skill).first()
                if skill_trend:
                    skill_trend.resumes_count += 1
                    skill_trend.total_mentions += 1
                    skill_trend.last_updated = datetime.utcnow()
                else:
                    skill_trend = SkillTrend(
                        skill_name=skill,
                        total_mentions=1,
                        resumes_count=1,
                        trend_score=1.0
                    )
                    db.session.add(skill_trend)
            
            db.session.commit()
            
            # Store information in session for recommendation
            session['extracted_skills'] = extracted_skills
            session['resume_filename'] = filename
            session['resume_id'] = resume.id
            session['user_id'] = user.id
            session['user_email'] = user_email
            
            return jsonify({
                'success': True,
                'skills': extracted_skills,
                'message': f'Successfully extracted {len(extracted_skills)} skills from your resume.'
            })
            
        except Exception as e:
            logging.error(f"Error extracting skills: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'Failed to process the resume. Please ensure the file is not corrupted and try again.'
            }), 500
        
        finally:
            # Clean up uploaded file
            try:
                if os.path.exists(filepath):
                    os.remove(filepath)
                    logging.info(f"Cleaned up file: {filepath}")
            except Exception as e:
                logging.warning(f"Failed to clean up file {filepath}: {str(e)}")
    
    except Exception as e:
        logging.error(f"Unexpected error in upload_resume: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'An unexpected error occurred. Please try again.'
        }), 500

@app.route('/recommend', methods=['GET'])
def recommend():
    """Get job recommendations based on extracted skills."""
    try:
        # Check if skills are available in session
        extracted_skills = session.get('extracted_skills')
        user_id = session.get('user_id')
        resume_id = session.get('resume_id')
        
        if not extracted_skills or not user_id or not resume_id:
            return jsonify({
                'success': False,
                'error': 'No skills found. Please upload a resume first.'
            }), 400
        
        # Get jobs from database
        jobs_query = Job.query.filter_by(is_active=True).all()
        jobs_data = []
        
        for job in jobs_query:
            job_skills = [skill.skill_name for skill in job.required_skills]
            job_data = {
                'id': job.id,
                'title': job.title,
                'company': job.company,
                'location': job.location,
                'experience_level': job.experience_level,
                'description': job.description,
                'required_skills': job_skills
            }
            jobs_data.append(job_data)
        
        # Get top 5 recommendations instead of 3
        recommendations = job_matcher.get_recommendations(extracted_skills, jobs_data, top_n=5)
        
        # Format response and save job applications
        formatted_recommendations = []
        for job_data, match_score, missing_skills in recommendations:
            # Calculate ATS score
            ats_score = job_matcher.calculate_ats_score(
                extracted_skills, 
                job_data['required_skills'], 
                job_data.get('description', '')
            )
            
            # Save job application to database
            job_application = JobApplication(
                user_id=user_id,
                resume_id=resume_id,
                job_id=job_data['id'],
                match_score=match_score,
                keyword_score=match_score,  # For now, using same score
                semantic_score=0.0,
                missing_skills_count=len(missing_skills),
                status='matched'
            )
            db.session.add(job_application)
            
            formatted_recommendations.append({
                'id': job_data['id'],
                'title': job_data['title'],
                'company': job_data['company'],
                'match_percentage': round(match_score * 100, 1),
                'ats_score': ats_score,
                'required_skills': job_data['required_skills'],
                'missing_skills': missing_skills,
                'description': job_data.get('description', ''),
                'location': job_data.get('location', ''),
                'experience_level': job_data.get('experience_level', '')
            })
        
        db.session.commit()
        
        # Send email notification for good matches (if user subscribed)
        user = User.query.get(user_id)
        if (user and user.email_notifications and 
            email_service.enabled and 
            formatted_recommendations):
            
            # Filter matches that meet notification threshold
            high_matches = [rec for rec in formatted_recommendations 
                           if rec['match_percentage'] >= user.notification_threshold]
            
            if high_matches:
                # Send email notification
                success = email_service.send_job_match_notification(
                    user.email, 
                    user.name, 
                    high_matches, 
                    extracted_skills
                )
                
                if success:
                    user.last_notification_sent = datetime.utcnow()
                    db.session.commit()
                    logging.info(f"Email notification sent to {user.email} for {len(high_matches)} matches")
        
        return jsonify({
            'success': True,
            'recommendations': formatted_recommendations,
            'user_skills': extracted_skills
        })
    
    except Exception as e:
        logging.error(f"Error in recommend: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to generate recommendations. Please try again.'
        }), 500

@app.route('/history', methods=['GET'])
def user_history():
    """Get user's resume upload and job match history."""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({
                'success': False,
                'error': 'No user session found. Please upload a resume first.'
            }), 400
        
        # Get user's resumes and applications
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                'success': False,
                'error': 'User not found.'
            }), 404
        
        resumes_data = []
        for resume in user.resumes:
            skills = [skill.skill_name for skill in resume.skills]
            applications = JobApplication.query.filter_by(resume_id=resume.id).all()
            
            resumes_data.append({
                'id': resume.id,
                'filename': resume.original_filename,
                'uploaded_at': resume.uploaded_at.isoformat() if resume.uploaded_at else None,
                'skills_count': len(skills),
                'skills': skills,
                'applications_count': len(applications)
            })
        
        return jsonify({
            'success': True,
            'user': {
                'name': user.name,
                'email': user.email,
                'member_since': user.created_at.isoformat() if user.created_at else None
            },
            'resumes': resumes_data,
            'total_resumes': len(resumes_data)
        })
    
    except Exception as e:
        logging.error(f"Error in user_history: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve user history.'
        }), 500

@app.route('/skills/trends', methods=['GET'])
def skill_trends():
    """Get trending skills analysis."""
    try:
        # Get top skills by popularity
        top_skills = SkillTrend.query.order_by(SkillTrend.total_mentions.desc()).limit(20).all()
        
        trends_data = []
        for skill in top_skills:
            trends_data.append({
                'skill_name': skill.skill_name,
                'total_mentions': skill.total_mentions,
                'resume_count': skill.resumes_count,
                'job_postings_count': skill.job_postings_count,
                'trend_score': skill.trend_score
            })
        
        # Get total statistics
        total_skills = SkillTrend.query.count()
        total_resumes = Resume.query.count()
        total_jobs = Job.query.filter_by(is_active=True).count()
        
        return jsonify({
            'success': True,
            'trending_skills': trends_data,
            'statistics': {
                'total_unique_skills': total_skills,
                'total_resumes_processed': total_resumes,
                'active_job_postings': total_jobs
            }
        })
    
    except Exception as e:
        logging.error(f"Error in skill_trends: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve skill trends.'
        }), 500

@app.route('/jobs', methods=['GET'])
def list_jobs():
    """Get all active job postings."""
    try:
        jobs = Job.query.filter_by(is_active=True).all()
        jobs_data = []
        
        for job in jobs:
            required_skills = [skill.skill_name for skill in job.required_skills]
            application_count = JobApplication.query.filter_by(job_id=job.id).count()
            
            jobs_data.append({
                'id': job.id,
                'title': job.title,
                'company': job.company,
                'location': job.location,
                'experience_level': job.experience_level,
                'description': job.description,
                'required_skills': required_skills,
                'application_count': application_count,
                'created_at': job.created_at.isoformat() if job.created_at else None
            })
        
        return jsonify({
            'success': True,
            'jobs': jobs_data,
            'total_jobs': len(jobs_data)
        })
    
    except Exception as e:
        logging.error(f"Error in list_jobs: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve job listings.'
        }), 500

# Subscription management endpoints
@app.route('/subscribe', methods=['POST'])
def subscribe():
    """Subscribe user to email notifications."""
    try:
        data = request.get_json() or {}
        email = data.get('email') or request.form.get('email')
        name = data.get('name') or request.form.get('name', 'User')
        threshold = data.get('threshold', 70)
        
        if not email:
            return jsonify({
                'success': False,
                'error': 'Email address is required.'
            }), 400
        
        # Find or create user
        user = User.query.filter_by(email=email).first()
        if user:
            # Update existing user subscription
            user.email_notifications = True
            user.notification_threshold = threshold
            user.subscribed_at = datetime.utcnow()
        else:
            # Create new user
            user = User(
                email=email,
                name=name,
                email_notifications=True,
                notification_threshold=threshold,
                subscribed_at=datetime.utcnow()
            )
            db.session.add(user)
        
        db.session.commit()
        
        # Send confirmation email
        if email_service.enabled:
            email_service.send_subscription_confirmation(email, name)
        
        return jsonify({
            'success': True,
            'message': f'Successfully subscribed {email} to job match notifications.',
            'threshold': threshold
        })
    
    except Exception as e:
        logging.error(f"Error in subscribe: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to subscribe. Please try again.'
        }), 500

@app.route('/unsubscribe', methods=['POST', 'GET'])
def unsubscribe():
    """Unsubscribe user from email notifications."""
    try:
        # Handle both POST (API) and GET (email link) requests
        if request.method == 'POST':
            data = request.get_json() or {}
            email = data.get('email') or request.form.get('email')
        else:  # GET request from email link
            email = request.args.get('email')
        
        if not email:
            return jsonify({
                'success': False,
                'error': 'Email address is required.'
            }), 400
        
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({
                'success': False,
                'error': 'Email address not found in our system.'
            }), 404
        
        user.email_notifications = False
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Successfully unsubscribed {email} from job notifications.'
        })
    
    except Exception as e:
        logging.error(f"Error in unsubscribe: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to unsubscribe. Please try again.'
        }), 500

@app.route('/subscription/status', methods=['GET'])
def subscription_status():
    """Get subscription status for current user."""
    try:
        user_email = session.get('user_email')
        if not user_email:
            return jsonify({
                'success': False,
                'error': 'No user session found.'
            }), 400
        
        user = User.query.filter_by(email=user_email).first()
        if not user:
            return jsonify({
                'success': True,
                'subscribed': False,
                'threshold': 70
            })
        
        return jsonify({
            'success': True,
            'subscribed': user.email_notifications,
            'threshold': user.notification_threshold,
            'email': user.email,
            'name': user.name,
            'subscribed_at': user.subscribed_at.isoformat() if user.subscribed_at else None,
            'last_notification': user.last_notification_sent.isoformat() if user.last_notification_sent else None
        })
    
    except Exception as e:
        logging.error(f"Error in subscription_status: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get subscription status.'
        }), 500

@app.route('/download_custom_resume', methods=['POST'])
def download_custom_resume():
    """Generate and download a custom resume optimized for a specific job"""
    try:
        # Get user email from session
        user_email = session.get('user_email')
        if not user_email:
            return jsonify({'error': 'User not found'}), 404
        
        # Get job ID from request
        data = request.get_json() or {}
        job_id = data.get('job_id')
        
        if not job_id:
            return jsonify({'error': 'Job ID is required'}), 400
        
        # Find user and their most recent resume
        user = User.query.filter_by(email=user_email).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        resume = Resume.query.filter_by(user_id=user.id).order_by(Resume.uploaded_at.desc()).first()
        if not resume:
            return jsonify({'error': 'No resume found'}), 404
        
        # Find job details
        job = Job.query.get(job_id)
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        
        # Get user skills and job requirements
        user_skills = [skill.skill_name for skill in ExtractedSkill.query.filter_by(resume_id=resume.id).all()]
        job_requirements = [skill.skill_name for skill in JobSkill.query.filter_by(job_id=job_id).all()]
        
        # Generate custom resume content
        custom_resume = generate_custom_resume_content(user, resume, job, user_skills, job_requirements)
        
        return jsonify({
            'success': True,
            'resume_content': custom_resume,
            'job_title': job.title,
            'company': job.company,
            'user_name': user.name
        })
        
    except Exception as e:
        logging.error(f"Error generating custom resume: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/fix_resume', methods=['POST'])
def fix_resume():
    """AI-enhanced resume improvements and suggestions"""
    try:
        # Get user email from session
        user_email = session.get('user_email')
        if not user_email:
            return jsonify({'error': 'User not found'}), 404
        
        # Find user and their most recent resume
        user = User.query.filter_by(email=user_email).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        resume = Resume.query.filter_by(user_id=user.id).order_by(Resume.uploaded_at.desc()).first()
        if not resume:
            return jsonify({'error': 'No resume found'}), 404
        
        # Get user skills
        user_skills = [skill.skill_name for skill in ExtractedSkill.query.filter_by(resume_id=resume.id).all()]
        
        # Generate AI-enhanced resume improvements
        improvements = generate_resume_improvements(user, resume, user_skills)
        
        return jsonify({
            'success': True,
            'improvements': improvements,
            'user_name': user.name,
            'skills_count': len(user_skills),
            'experience_years': resume.experience_years,
            'education_level': resume.education_level
        })
        
    except Exception as e:
        logging.error(f"Error generating resume improvements: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/resume_builder', methods=['POST'])
def resume_builder():
    """Interactive resume builder with step-by-step guidance"""
    try:
        # Get user email from session
        user_email = session.get('user_email')
        if not user_email:
            return jsonify({'error': 'User not found'}), 404
        
        # Get request data
        data = request.get_json() or {}
        step = data.get('step', 'start')
        form_data = data.get('data', {})
        
        user = User.query.filter_by(email=user_email).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Generate resume builder response based on step
        builder_response = generate_resume_builder_response(user, step, form_data)
        
        return jsonify({
            'success': True,
            'response': builder_response,
            'user_name': user.name
        })
        
    except Exception as e:
        logging.error(f"Error in resume builder: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/cover_letter', methods=['POST'])
def generate_cover_letter():
    """AI-powered cover letter generator"""
    try:
        # Get user email from session
        user_email = session.get('user_email')
        if not user_email:
            return jsonify({'error': 'User not found'}), 404
        
        # Get request data
        data = request.get_json() or {}
        job_id = data.get('job_id')
        company_name = data.get('company_name', '')
        job_title = data.get('job_title', '')
        
        user = User.query.filter_by(email=user_email).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get user's resume and skills
        resume = Resume.query.filter_by(user_id=user.id).order_by(Resume.uploaded_at.desc()).first()
        if not resume:
            return jsonify({'error': 'Please upload a resume first'}), 404
        
        user_skills = [skill.skill_name for skill in ExtractedSkill.query.filter_by(resume_id=resume.id).all()]
        
        # Generate cover letter
        if job_id:
            job = Job.query.get(job_id)
            if job:
                company_name = job.company
                job_title = job.title
        
        cover_letter = generate_ai_cover_letter(user, resume, user_skills, company_name, job_title)
        
        return jsonify({
            'success': True,
            'cover_letter': cover_letter,
            'company_name': company_name,
            'job_title': job_title,
            'user_name': user.name
        })
        
    except Exception as e:
        logging.error(f"Error generating cover letter: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/pdf_editor', methods=['POST'])
def pdf_editor():
    """PDF resume editor functionality"""
    try:
        # Get user email from session
        user_email = session.get('user_email')
        if not user_email:
            return jsonify({'error': 'User not found'}), 404
        
        # Get request data
        data = request.get_json() or {}
        action = data.get('action', 'load')
        
        user = User.query.filter_by(email=user_email).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get user's most recent resume
        resume = Resume.query.filter_by(user_id=user.id).order_by(Resume.uploaded_at.desc()).first()
        if not resume:
            return jsonify({'error': 'Please upload a resume first'}), 404
        
        # Generate PDF editor interface
        editor_response = generate_pdf_editor_interface(user, resume, action, data)
        
        return jsonify({
            'success': True,
            'response': editor_response,
            'user_name': user.name
        })
        
    except Exception as e:
        logging.error(f"Error in PDF editor: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/career_chat', methods=['POST'])
def career_chat():
    """AI-powered career assistant chatbot"""
    try:
        # Get request data
        data = request.get_json() or {}
        message = data.get('message', '')
        conversation_history = data.get('history', [])
        
        # Get user email from session (optional)
        user_email = session.get('user_email')
        user = None
        resume = None
        user_skills = []
        
        if user_email:
            user = User.query.filter_by(email=user_email).first()
            if user:
                # Get user context (resume, skills, etc.)
                resume = Resume.query.filter_by(user_id=user.id).order_by(Resume.uploaded_at.desc()).first()
                if resume:
                    user_skills = [skill.skill_name for skill in ExtractedSkill.query.filter_by(resume_id=resume.id).all()]
        
        # Generate AI response
        chat_response = generate_career_chat_response(user, resume, user_skills, message, conversation_history)
        
        return jsonify({
            'success': True,
            'response': chat_response,
            'user_name': user.name if user else 'Guest'
        })
        
    except Exception as e:
        logging.error(f"Error in career chat: {e}")
        return jsonify({'error': str(e)}), 500

def generate_custom_resume_content(user, resume, job, user_skills, job_requirements):
    """Generate AI-optimized resume content for a specific job"""
    
    # Calculate skill match and identify missing skills
    matching_skills = set(user_skills) & set(job_requirements)
    missing_skills = set(job_requirements) - set(user_skills)
    match_percentage = len(matching_skills) / len(job_requirements) * 100 if job_requirements else 0
    
    # Generate optimized resume sections
    custom_content = {
        'header': {
            'name': user.name,
            'email': user.email,
            'target_role': job.title,
            'target_company': job.company
        },
        'summary': generate_tailored_summary(user, job, matching_skills, resume.experience_years),
        'skills': {
            'highlighted': list(matching_skills),
            'additional': [skill for skill in user_skills if skill not in matching_skills],
            'recommendations': list(missing_skills)[:3]  # Top 3 missing skills
        },
        'optimization_tips': [
            f"Emphasize your {len(matching_skills)} matching skills prominently",
            f"Consider learning {', '.join(list(missing_skills)[:2])} to boost your match from {match_percentage:.1f}%",
            f"Highlight experience with {', '.join(list(matching_skills)[:3])} early in your summary",
            "Use keywords from the job description throughout your resume",
            "Quantify achievements with specific numbers and results"
        ],
        'match_analysis': {
            'score': match_percentage,
            'matching_skills_count': len(matching_skills),
            'missing_skills_count': len(missing_skills),
            'total_requirements': len(job_requirements)
        }
    }
    
    return custom_content

def generate_tailored_summary(user, job, matching_skills, experience_years):
    """Generate a tailored professional summary"""
    
    # Create experience level description
    if experience_years >= 5:
        experience_desc = f"seasoned professional with {experience_years}+ years"
    elif experience_years >= 2:
        experience_desc = f"experienced developer with {experience_years} years"
    else:
        experience_desc = "motivated professional"
    
    # Create skills highlight
    skills_highlight = ', '.join(list(matching_skills)[:4]) if matching_skills else "various technical skills"
    
    summary = f"""Dynamic and {experience_desc} of experience specializing in {skills_highlight}. 
    Proven track record of delivering high-quality solutions and contributing to successful project outcomes. 
    Passionate about {job.title.lower()} roles and eager to bring expertise to {job.company}. 
    Strong problem-solving abilities with a focus on continuous learning and innovation."""
    
    return summary.strip()

def generate_resume_improvements(user, resume, user_skills):
    """Generate AI-enhanced resume improvements and suggestions"""
    
    # Analyze current resume strengths and areas for improvement
    improvements = {
        'overall_score': calculate_resume_score(resume, user_skills),
        'strengths': identify_resume_strengths(resume, user_skills),
        'improvements': suggest_resume_improvements(resume, user_skills),
        'skill_recommendations': get_skill_recommendations(user_skills),
        'formatting_tips': get_formatting_recommendations(),
        'market_insights': get_market_insights(user_skills)
    }
    
    return improvements

def calculate_resume_score(resume, user_skills):
    """Calculate overall resume score out of 100"""
    score = 0
    
    # Skills diversity (0-30 points)
    skills_score = min(len(user_skills) * 2, 30)
    score += skills_score
    
    # Experience level (0-25 points) 
    experience_score = min(resume.experience_years * 3, 25)
    score += experience_score
    
    # Education (0-15 points)
    education_score = 15 if resume.education_level and resume.education_level != 'Not Specified' else 5
    score += education_score
    
    # Projects and certifications (0-20 points)
    projects_score = min(resume.projects_count * 4, 15)
    cert_score = 5 if resume.certifications else 0
    score += projects_score + cert_score
    
    # Skills confidence (0-10 points)
    confidence_score = int(resume.skills_confidence * 10) if resume.skills_confidence else 5
    score += confidence_score
    
    return min(score, 100)

def identify_resume_strengths(resume, user_skills):
    """Identify key strengths in the resume"""
    strengths = []
    
    if len(user_skills) >= 10:
        strengths.append(f"Diverse skill set with {len(user_skills)} technical skills")
    
    if resume.experience_years >= 3:
        strengths.append(f"Solid experience with {resume.experience_years} years in the field")
    
    if resume.projects_count >= 3:
        strengths.append(f"Strong project portfolio with {resume.projects_count} completed projects")
    
    if resume.certifications:
        strengths.append("Professional certifications demonstrate commitment to learning")
    
    # Check for in-demand skills
    hot_skills = {'python', 'javascript', 'react', 'aws', 'docker', 'kubernetes', 'machine learning', 'data science'}
    user_hot_skills = set(skill.lower() for skill in user_skills) & hot_skills
    if user_hot_skills:
        strengths.append(f"Proficiency in high-demand skills: {', '.join(user_hot_skills)}")
    
    return strengths if strengths else ["Shows potential for growth and development"]

def suggest_resume_improvements(resume, user_skills):
    """Suggest specific improvements for the resume"""
    suggestions = []
    
    if len(user_skills) < 8:
        suggestions.append("Expand your skill set - aim for 10+ relevant technical skills")
    
    if resume.experience_years < 2:
        suggestions.append("Highlight internships, freelance work, or personal projects to show experience")
    
    if resume.projects_count < 3:
        suggestions.append("Add more project examples with specific achievements and technologies used")
    
    if not resume.certifications or resume.certifications.strip() == "":
        suggestions.append("Consider obtaining relevant certifications to validate your skills")
    
    if resume.skills_confidence < 0.7:
        suggestions.append("Focus on building deeper expertise in your core skills")
    
    # Technical suggestions
    suggestions.extend([
        "Use action verbs to start each bullet point (Developed, Implemented, Optimized)",
        "Quantify achievements with specific numbers and percentages",
        "Include keywords from job postings you're targeting",
        "Keep your resume to 1-2 pages with consistent formatting",
        "Add a professional summary highlighting your key strengths"
    ])
    
    return suggestions

def get_skill_recommendations(user_skills):
    """Recommend skills to learn based on current skills and market trends"""
    recommendations = []
    user_skills_lower = [skill.lower() for skill in user_skills]
    
    # Programming language recommendations
    if 'python' in user_skills_lower and 'machine learning' not in user_skills_lower:
        recommendations.append("Machine Learning - High demand with Python background")
    
    if 'javascript' in user_skills_lower and 'typescript' not in user_skills_lower:
        recommendations.append("TypeScript - Industry standard for JavaScript development")
    
    if 'react' in user_skills_lower and 'next.js' not in user_skills_lower:
        recommendations.append("Next.js - Popular React framework for production apps")
    
    # Cloud and DevOps
    if 'aws' not in user_skills_lower and 'azure' not in user_skills_lower:
        recommendations.append("AWS or Azure - Essential cloud platforms for modern development")
    
    if 'docker' not in user_skills_lower:
        recommendations.append("Docker - Containerization is crucial for deployment")
    
    # Database recommendations
    if 'postgresql' in user_skills_lower and 'mongodb' not in user_skills_lower:
        recommendations.append("MongoDB - NoSQL database skills complement SQL knowledge")
    
    return recommendations[:5]  # Return top 5 recommendations

def get_formatting_recommendations():
    """Provide resume formatting best practices"""
    return [
        "Use a clean, professional font like Arial or Calibri (11-12pt)",
        "Maintain consistent spacing and alignment throughout",
        "Use bullet points instead of paragraphs for easy scanning",
        "Include plenty of white space for readability",
        "Use bold text sparingly to highlight key information",
        "Save and send as PDF to preserve formatting",
        "Ensure your contact information is prominently displayed"
    ]

def get_market_insights(user_skills):
    """Provide market insights based on user's skills"""
    user_skills_lower = [skill.lower() for skill in user_skills]
    insights = []
    
    # Tech market insights
    if 'python' in user_skills_lower:
        insights.append("Python developers see 25% higher salaries than average")
    
    if 'react' in user_skills_lower:
        insights.append("React is the most in-demand frontend framework in 2024")
    
    if 'aws' in user_skills_lower:
        insights.append("AWS certification can increase salary by 15-30%")
    
    if 'machine learning' in user_skills_lower:
        insights.append("ML engineers are among the highest-paid tech roles")
    
    # General insights
    insights.extend([
        "Remote work opportunities increased by 400% since 2020",
        "Companies prioritize full-stack developers over specialists",
        "Open source contributions significantly boost hiring chances"
    ])
    
    return insights[:4]  # Return top 4 insights

def generate_resume_builder_response(user, step, form_data):
    """Generate step-by-step resume builder guidance"""
    
    if step == 'start':
        return {
            'step': 'personal_info',
            'title': 'Personal Information',
            'description': 'Let\'s start with your basic information',
            'fields': [
                {'name': 'full_name', 'label': 'Full Name', 'type': 'text', 'required': True, 'value': user.name or ''},
                {'name': 'email', 'label': 'Email Address', 'type': 'email', 'required': True, 'value': user.email or ''},
                {'name': 'phone', 'label': 'Phone Number', 'type': 'tel', 'required': True, 'value': ''},
                {'name': 'location', 'label': 'Location (City, State)', 'type': 'text', 'required': True, 'value': ''},
                {'name': 'linkedin', 'label': 'LinkedIn Profile', 'type': 'url', 'required': False, 'value': ''},
                {'name': 'portfolio', 'label': 'Portfolio Website', 'type': 'url', 'required': False, 'value': ''}
            ],
            'tips': [
                'Use a professional email address',
                'Include your LinkedIn profile if available',
                'Ensure your contact information is current'
            ]
        }
    
    elif step == 'professional_summary':
        return {
            'step': 'experience',
            'title': 'Professional Summary',
            'description': 'Write a compelling summary of your professional background',
            'fields': [
                {'name': 'summary', 'label': 'Professional Summary', 'type': 'textarea', 'required': True, 'placeholder': 'Write 2-3 sentences highlighting your key skills and experience...'}
            ],
            'sample': f"Experienced professional with expertise in {', '.join(get_user_top_skills(user)[:3])}. Proven track record of delivering high-quality solutions and contributing to successful projects. Passionate about continuous learning and innovation in the tech industry.",
            'tips': [
                'Keep it concise (2-4 sentences)',
                'Highlight your most relevant skills',
                'Include years of experience if applicable',
                'Tailor it to your target role'
            ]
        }
    
    elif step == 'experience':
        return {
            'step': 'education',
            'title': 'Work Experience',
            'description': 'Add your work experience in reverse chronological order',
            'fields': [
                {'name': 'job_title', 'label': 'Job Title', 'type': 'text', 'required': True},
                {'name': 'company', 'label': 'Company Name', 'type': 'text', 'required': True},
                {'name': 'location', 'label': 'Location', 'type': 'text', 'required': True},
                {'name': 'start_date', 'label': 'Start Date', 'type': 'month', 'required': True},
                {'name': 'end_date', 'label': 'End Date', 'type': 'month', 'required': False, 'placeholder': 'Leave blank if current'},
                {'name': 'description', 'label': 'Job Description', 'type': 'textarea', 'required': True, 'placeholder': 'Describe your key responsibilities and achievements...'}
            ],
            'tips': [
                'Start with action verbs (Developed, Managed, Led)',
                'Quantify achievements with numbers when possible',
                'Focus on accomplishments, not just duties',
                'Include 3-5 bullet points per role'
            ]
        }
    
    elif step == 'education':
        return {
            'step': 'skills',
            'title': 'Education',
            'description': 'Add your educational background',
            'fields': [
                {'name': 'degree', 'label': 'Degree', 'type': 'text', 'required': True, 'placeholder': 'e.g., Bachelor of Science'},
                {'name': 'major', 'label': 'Major/Field of Study', 'type': 'text', 'required': True},
                {'name': 'school', 'label': 'School/University', 'type': 'text', 'required': True},
                {'name': 'graduation_year', 'label': 'Graduation Year', 'type': 'number', 'required': True},
                {'name': 'gpa', 'label': 'GPA', 'type': 'number', 'required': False, 'placeholder': 'Optional - include if 3.5+'}
            ],
            'tips': [
                'Include relevant coursework if recent graduate',
                'Only include GPA if 3.5 or higher',
                'Add honors or awards if applicable'
            ]
        }
    
    elif step == 'skills':
        user_skills = get_user_top_skills(user)
        return {
            'step': 'complete',
            'title': 'Skills & Technologies',
            'description': 'Select and organize your technical skills',
            'suggested_skills': user_skills,
            'skill_categories': {
                'Programming Languages': ['Python', 'JavaScript', 'Java', 'C++', 'C#', 'PHP', 'Ruby', 'Go'],
                'Web Technologies': ['HTML', 'CSS', 'React', 'Angular', 'Vue.js', 'Node.js', 'Express'],
                'Databases': ['MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'SQLite'],
                'Cloud & DevOps': ['AWS', 'Azure', 'Docker', 'Kubernetes', 'Jenkins', 'Git'],
                'Tools & Frameworks': ['Django', 'Flask', 'Spring', 'Laravel', 'Bootstrap']
            },
            'tips': [
                'Organize skills by category',
                'List most relevant skills first',
                'Be honest about your skill level',
                'Include both technical and soft skills'
            ]
        }
    
    return {'step': 'complete', 'title': 'Resume Complete!', 'description': 'Your resume is ready for download'}

def generate_ai_cover_letter(user, resume, user_skills, company_name, job_title):
    """Generate AI-powered cover letter"""
    
    # Create experience description
    experience_years = resume.experience_years or 2
    if experience_years >= 5:
        experience_desc = f"seasoned professional with {experience_years}+ years of experience"
    elif experience_years >= 2:
        experience_desc = f"experienced professional with {experience_years} years of experience"
    else:
        experience_desc = "motivated professional"
    
    # Get top skills for the letter
    top_skills = user_skills[:4] if user_skills else ['software development', 'problem-solving']
    skills_text = ', '.join(top_skills)
    
    # Generate personalized cover letter
    cover_letter = {
        'header': {
            'date': datetime.utcnow().strftime('%B %d, %Y'),
            'recipient': f"Hiring Manager\n{company_name}" if company_name else "Hiring Manager",
            'subject': f"Application for {job_title} Position" if job_title else "Job Application"
        },
        'opening': f"Dear Hiring Manager,\n\nI am writing to express my strong interest in the {job_title or 'position'} role at {company_name or 'your company'}. As a {experience_desc} specializing in {skills_text}, I am excited about the opportunity to contribute to your team's success.",
        'body': [
            f"In my {experience_years} years of professional experience, I have developed expertise in {skills_text}. My background has equipped me with strong problem-solving abilities and a passion for delivering high-quality solutions that drive business results.",
            f"What particularly attracts me to {company_name or 'your company'} is the opportunity to work on innovative projects and contribute to a forward-thinking organization. I am confident that my skills in {', '.join(top_skills[:2])} and my commitment to continuous learning make me an ideal candidate for this role.",
            "I would welcome the opportunity to discuss how my experience and enthusiasm can contribute to your team. Thank you for considering my application. I look forward to hearing from you soon."
        ],
        'closing': f"Sincerely,\n{user.name}",
        'tips': [
            'Customize the opening paragraph for each application',
            'Research the company and mention specific details',
            'Quantify your achievements when possible',
            'Keep it to one page and professional tone',
            'Proofread carefully before sending'
        ]
    }
    
    return cover_letter

def generate_pdf_editor_interface(user, resume, action, data):
    """Generate PDF editor interface and functionality"""
    
    if action == 'load':
        return {
            'action': 'load',
            'title': 'PDF Resume Editor',
            'description': 'Edit your resume content directly',
            'current_resume': {
                'filename': resume.original_filename,
                'upload_date': resume.uploaded_at.strftime('%B %d, %Y') if resume.uploaded_at else 'Unknown',
                'file_size': f"{resume.file_size / 1024:.1f} KB" if resume.file_size else 'Unknown'
            },
            'sections': [
                {
                    'name': 'Contact Information',
                    'icon': 'fas fa-user',
                    'content': f"Name: {user.name}\nEmail: {user.email}",
                    'editable': True
                },
                {
                    'name': 'Professional Summary',
                    'icon': 'fas fa-file-text',
                    'content': generate_summary_from_skills(user, get_user_top_skills(user)),
                    'editable': True
                },
                {
                    'name': 'Technical Skills',
                    'icon': 'fas fa-code',
                    'content': ', '.join(get_user_top_skills(user)),
                    'editable': True
                },
                {
                    'name': 'Experience',
                    'icon': 'fas fa-briefcase',
                    'content': f"Experience Level: {resume.experience_years or 'Not specified'} years\nEducation: {resume.education_level or 'Not specified'}",
                    'editable': True
                }
            ],
            'tools': [
                {'name': 'Bold Text', 'icon': 'fas fa-bold', 'action': 'bold'},
                {'name': 'Italic Text', 'icon': 'fas fa-italic', 'action': 'italic'},
                {'name': 'Bullet Points', 'icon': 'fas fa-list-ul', 'action': 'bullets'},
                {'name': 'Export PDF', 'icon': 'fas fa-file-pdf', 'action': 'export'}
            ],
            'templates': [
                {'name': 'Modern', 'preview': 'Clean and contemporary design'},
                {'name': 'Professional', 'preview': 'Traditional business format'},
                {'name': 'Creative', 'preview': 'Eye-catching design with colors'},
                {'name': 'Minimal', 'preview': 'Simple and elegant layout'}
            ]
        }
    
    elif action == 'edit':
        section = data.get('section', '')
        content = data.get('content', '')
        return {
            'action': 'edit',
            'message': f'Successfully updated {section} section',
            'updated_content': content,
            'suggestions': [
                'Use action verbs to start bullet points',
                'Quantify achievements with specific numbers',
                'Keep descriptions concise and impactful'
            ]
        }
    
    elif action == 'export':
        template = data.get('template', 'Modern')
        return {
            'action': 'export',
            'message': f'Resume exported with {template} template',
            'download_url': '/download_resume_pdf',
            'filename': f"{user.name.replace(' ', '_')}_Resume_{template}.pdf"
        }
    
    return {'action': 'unknown', 'message': 'Unknown action'}

def generate_career_chat_response(user, resume, user_skills, message, conversation_history):
    """Generate AI-powered career assistant responses"""
    
    # Analyze the user's message intent
    message_lower = message.lower()
    
    # Get user context safely
    user_name = user.name if user else 'there'
    experience_years = resume.experience_years if resume else 0
    education_level = resume.education_level if resume else 'Not specified'
    skills_count = len(user_skills)
    
    # Generate contextual response based on message intent
    if any(word in message_lower for word in ['salary', 'pay', 'compensation', 'money']):
        response = generate_salary_advice(user_skills, experience_years)
    elif any(word in message_lower for word in ['interview', 'questions', 'prepare']):
        response = generate_interview_advice(user_skills, user.name)
    elif any(word in message_lower for word in ['career', 'path', 'growth', 'future']):
        response = generate_career_path_advice(user_skills, experience_years)
    elif any(word in message_lower for word in ['skills', 'learn', 'improve', 'develop']):
        response = generate_skill_advice(user_skills)
    elif any(word in message_lower for word in ['resume', 'cv', 'application']):
        response = generate_resume_advice(user, resume, user_skills)
    elif any(word in message_lower for word in ['job', 'search', 'hunting', 'apply']):
        response = generate_job_search_advice(user_skills, experience_years)
    else:
        response = generate_general_career_advice(user_name, user_skills, experience_years)
    
    return {
        'message': response['text'],
        'suggestions': response.get('suggestions', []),
        'resources': response.get('resources', []),
        'user_context': {
            'name': user_name,
            'skills_count': skills_count,
            'experience_years': experience_years,
            'education_level': education_level
        }
    }

def get_user_top_skills(user):
    """Get user's top skills from their resume"""
    if not user:
        return ['Python', 'JavaScript', 'HTML', 'CSS', 'Git']  # Default skills
    
    try:
        resume = Resume.query.filter_by(user_id=user.id).order_by(Resume.uploaded_at.desc()).first()
        if resume:
            skills = [skill.skill_name for skill in ExtractedSkill.query.filter_by(resume_id=resume.id).all()]
            return skills[:10]  # Return top 10 skills
        return ['Python', 'JavaScript', 'HTML', 'CSS', 'Git']  # Default skills
    except Exception:
        return ['Python', 'JavaScript', 'HTML', 'CSS', 'Git']  # Default skills

def generate_summary_from_skills(user, skills):
    """Generate a professional summary from user skills"""
    if not skills:
        return "Motivated professional with a passion for technology and continuous learning."
    
    top_skills = skills[:3]
    return f"Experienced professional specializing in {', '.join(top_skills)}. Strong background in software development with proven ability to deliver high-quality solutions and contribute to team success."

def generate_salary_advice(user_skills, experience_years):
    """Generate salary negotiation advice"""
    skills_text = ', '.join(user_skills[:3]) if user_skills else 'your skills'
    
    return {
        'text': f"Based on your {experience_years} years of experience and skills in {skills_text}, here's my salary advice:\n\n"
                f"• Research market rates on Glassdoor, PayScale, and LinkedIn Salary\n"
                f"• With {experience_years} years experience, you're likely in the {'senior' if experience_years >= 5 else 'mid-level' if experience_years >= 2 else 'junior'} range\n"
                f"• Negotiate based on your specific achievements and impact\n"
                f"• Consider the full compensation package, not just base salary",
        'suggestions': [
            'Research industry standards for your role',
            'Document your achievements with specific metrics',
            'Practice your negotiation conversation',
            'Consider remote work for higher-paying markets'
        ],
        'resources': [
            'Glassdoor Salary Tool',
            'PayScale Compensation Data',
            'LinkedIn Salary Insights'
        ]
    }

def generate_interview_advice(user_skills, user_name):
    """Generate interview preparation advice"""
    return {
        'text': f"Hi {user_name}! Here's how to ace your next interview:\n\n"
                f"• Prepare STAR (Situation, Task, Action, Result) stories for your key projects\n"
                f"• Review common technical questions for your skill set\n"
                f"• Research the company's mission, values, and recent news\n"
                f"• Prepare thoughtful questions about the role and team\n"
                f"• Practice coding problems if it's a technical role",
        'suggestions': [
            'Mock interview with a friend or mentor',
            'Prepare 3-5 STAR method examples',
            'Research your interviewer on LinkedIn',
            'Plan your outfit and route in advance'
        ],
        'resources': [
            'LeetCode for coding practice',
            'Glassdoor for company reviews',
            'Pramp for mock interviews'
        ]
    }

def generate_career_path_advice(user_skills, experience_years):
    """Generate career progression advice"""
    return {
        'text': f"With {experience_years} years of experience, here's your career growth roadmap:\n\n"
                f"• Focus on developing leadership and mentoring skills\n"
                f"• Consider specializing in high-demand areas like AI, cloud, or cybersecurity\n"
                f"• Build your professional network through conferences and meetups\n"
                f"• Seek opportunities to lead projects or mentor junior developers\n"
                f"• Consider pursuing relevant certifications or advanced degrees",
        'suggestions': [
            'Set clear 1-year and 5-year career goals',
            'Find a mentor in your target role',
            'Contribute to open source projects',
            'Speak at conferences or write technical blogs'
        ],
        'resources': [
            'Professional associations in your field',
            'Industry conferences and meetups',
            'LinkedIn Learning courses'
        ]
    }

def generate_skill_advice(user_skills):
    """Generate skill development advice"""
    hot_skills = ['AI/Machine Learning', 'Cloud Computing', 'Cybersecurity', 'Data Science', 'DevOps']
    recommended = [skill for skill in hot_skills if skill.lower() not in [s.lower() for s in user_skills]][:3]
    
    return {
        'text': f"Based on current market trends, here are skills to consider developing:\n\n"
                f"• {', '.join(recommended)} are in high demand\n"
                f"• Focus on cloud platforms (AWS, Azure, GCP) for better opportunities\n"
                f"• Soft skills like communication and leadership are equally important\n"
                f"• Stay updated with industry blogs and podcasts",
        'suggestions': [
            'Take online courses on Coursera or Udemy',
            'Build projects to demonstrate new skills',
            'Join communities like Stack Overflow or Reddit',
            'Attend workshops and bootcamps'
        ],
        'resources': [
            'Free Code Camp',
            'Coursera and edX courses',
            'YouTube tutorials'
        ]
    }

def generate_resume_advice(user, resume, user_skills):
    """Generate resume improvement advice"""
    skills_count = len(user_skills)
    
    return {
        'text': f"Here's how to improve your resume:\n\n"
                f"• You have {skills_count} skills listed - aim for 10-15 relevant ones\n"
                f"• Use action verbs: 'Developed', 'Implemented', 'Led', 'Optimized'\n"
                f"• Quantify achievements: '30% performance improvement', '500+ users'\n"
                f"• Tailor your resume for each job application\n"
                f"• Use a clean, professional format",
        'suggestions': [
            'Add metrics to demonstrate impact',
            'Include relevant projects and portfolios',
            'Keep it to 1-2 pages maximum',
            'Use keywords from job descriptions'
        ],
        'resources': [
            'Resume templates on Canva',
            'ATS-friendly formats',
            'Industry-specific resume guides'
        ]
    }

def generate_job_search_advice(user_skills, experience_years):
    """Generate job search strategy advice"""
    return {
        'text': f"Effective job search strategy for your {experience_years} years of experience:\n\n"
                f"• Apply to 10-15 jobs per week, not 50+ low-quality applications\n"
                f"• Network actively - 70% of jobs aren't publicly posted\n"
                f"• Use multiple job boards: LinkedIn, Indeed, company websites\n"
                f"• Follow up on applications after 1-2 weeks\n"
                f"• Consider working with recruiters in your field",
        'suggestions': [
            'Set up job alerts with specific keywords',
            'Optimize your LinkedIn profile',
            'Ask for referrals from your network',
            'Track your applications in a spreadsheet'
        ],
        'resources': [
            'LinkedIn Premium for job insights',
            'Company career pages',
            'Industry-specific job boards'
        ]
    }

def generate_general_career_advice(user_name, user_skills, experience_years):
    """Generate general career guidance"""
    return {
        'text': f"Hi {user_name}! I'm here to help with your career questions.\n\n"
                f"With your background in {', '.join(user_skills[:3]) if user_skills else 'technology'} "
                f"and {experience_years} years of experience, you have great potential!\n\n"
                f"I can help you with:\n"
                f"• Resume optimization and interview preparation\n"
                f"• Salary negotiation and career growth\n"
                f"• Skill development and learning paths\n"
                f"• Job search strategies and networking\n\n"
                f"What specific career topic would you like to discuss?",
        'suggestions': [
            'Ask about salary ranges for your skills',
            'Get interview preparation tips',
            'Discuss career growth opportunities',
            'Learn about in-demand skills to develop'
        ],
        'resources': [
            'Career development articles',
            'Industry trend reports',
            'Professional networking events'
        ]
    }

@app.errorhandler(413)
def too_large(e):
    """Handle file too large error."""
    return jsonify({
        'success': False,
        'error': 'File too large. Please upload a file smaller than 16MB.'
    }), 413

@app.errorhandler(500)
def internal_error(e):
    """Handle internal server errors."""
    logging.error(f"Internal server error: {str(e)}")
    return jsonify({
        'success': False,
        'error': 'An internal server error occurred. Please try again later.'
    }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
