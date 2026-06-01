"""Email service for sending job match notifications using SendGrid."""
import os
import logging
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
from typing import List, Dict

class EmailService:
    """Handle email notifications for job matches."""
    
    def __init__(self):
        """Initialize SendGrid client."""
        self.api_key = os.environ.get('SENDGRID_API_KEY')
        if not self.api_key:
            logging.warning("SENDGRID_API_KEY not found, email notifications disabled")
            self.enabled = False
        else:
            self.sg = SendGridAPIClient(self.api_key)
            self.enabled = True
            logging.info("Email service initialized with SendGrid")
    
    def send_job_match_notification(self, user_email: str, user_name: str, job_matches: List[Dict], user_skills: List[str]) -> bool:
        """Send job match notification email to user."""
        if not self.enabled:
            logging.warning("Email service disabled, cannot send notification")
            return False
        
        try:
            # Create email content
            subject = f"🎯 {len(job_matches)} New Job Matches Found - AI Job Matcher"
            
            # Generate HTML content
            html_content = self._generate_job_match_html(user_name, job_matches, user_skills)
            
            # Generate plain text content
            text_content = self._generate_job_match_text(user_name, job_matches, user_skills)
            
            # Create email
            message = Mail(
                from_email=Email("noreply@jobmatcher.ai", "AI Job Matcher"),
                to_emails=To(user_email),
                subject=subject,
                html_content=Content("text/html", html_content),
                plain_text_content=Content("text/plain", text_content)
            )
            
            # Send email
            response = self.sg.send(message)
            
            if response.status_code in [200, 201, 202]:
                logging.info(f"Job match notification sent to {user_email}")
                return True
            else:
                logging.error(f"Failed to send email: {response.status_code}")
                return False
                
        except Exception as e:
            logging.error(f"Error sending job match notification: {e}")
            return False
    
    def send_subscription_confirmation(self, user_email: str, user_name: str) -> bool:
        """Send subscription confirmation email."""
        if not self.enabled:
            return False
        
        try:
            subject = "Welcome to AI Job Matcher - Subscription Confirmed"
            
            html_content = f"""
            <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; text-align: center;">
                    <h1 style="color: white; margin: 0;">🤖 AI Job Matcher</h1>
                </div>
                
                <div style="padding: 30px; background-color: #f8f9ff;">
                    <h2 style="color: #333;">Welcome, {user_name}!</h2>
                    
                    <p>Thank you for subscribing to AI Job Matcher notifications. You'll now receive automatic email alerts when we find job opportunities that match your skills.</p>
                    
                    <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0;">
                        <h3 style="color: #667eea;">What you'll receive:</h3>
                        <ul style="color: #555;">
                            <li>📧 Instant notifications for high-match jobs (70%+ compatibility)</li>
                            <li>📊 Weekly summary of new opportunities</li>
                            <li>🎯 Personalized skill recommendations</li>
                            <li>📈 Market trend insights</li>
                        </ul>
                    </div>
                    
                    <p style="color: #666;">Keep your resume updated to ensure the best job matches!</p>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="https://your-app-url.com" style="background: #667eea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 6px; display: inline-block;">Visit AI Job Matcher</a>
                    </div>
                </div>
                
                <div style="background: #f0f0f0; padding: 15px; text-align: center; font-size: 12px; color: #666;">
                    <p>You can unsubscribe from these notifications at any time by visiting your profile settings.</p>
                </div>
            </body>
            </html>
            """
            
            text_content = f"""
            Welcome to AI Job Matcher, {user_name}!
            
            Thank you for subscribing to job match notifications. You'll now receive automatic email alerts when we find opportunities that match your skills.
            
            What you'll receive:
            - Instant notifications for high-match jobs (70%+ compatibility)
            - Weekly summary of new opportunities  
            - Personalized skill recommendations
            - Market trend insights
            
            Keep your resume updated to ensure the best job matches!
            
            Visit: https://your-app-url.com
            
            You can unsubscribe at any time from your profile settings.
            """
            
            message = Mail(
                from_email=Email("noreply@jobmatcher.ai", "AI Job Matcher"),
                to_emails=To(user_email),
                subject=subject,
                html_content=Content("text/html", html_content),
                plain_text_content=Content("text/plain", text_content)
            )
            
            response = self.sg.send(message)
            return response.status_code in [200, 201, 202]
            
        except Exception as e:
            logging.error(f"Error sending subscription confirmation: {e}")
            return False
    
    def _generate_job_match_html(self, user_name: str, job_matches: List[Dict], user_skills: List[str]) -> str:
        """Generate HTML content for job match notification."""
        
        # Generate job cards HTML
        job_cards_html = ""
        for i, job in enumerate(job_matches[:3], 1):  # Top 3 matches
            match_color = "#28a745" if job['match_percentage'] >= 70 else "#ffc107" if job['match_percentage'] >= 50 else "#dc3545"
            ats_color = "#28a745" if job['ats_score'] >= 70 else "#ffc107" if job['ats_score'] >= 50 else "#dc3545"
            
            missing_skills_html = ""
            if job['missing_skills']:
                missing_skills_html = f"""
                <div style="margin-top: 10px;">
                    <strong style="color: #e74c3c;">Skills to develop:</strong>
                    <div style="margin-top: 5px;">
                        {', '.join(job['missing_skills'][:5])}
                        {' and more...' if len(job['missing_skills']) > 5 else ''}
                    </div>
                </div>
                """
            
            job_cards_html += f"""
            <div style="background: white; border-radius: 8px; padding: 20px; margin: 15px 0; border-left: 4px solid {match_color};">
                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 15px;">
                    <div>
                        <h3 style="margin: 0; color: #333; font-size: 18px;">{job['title']}</h3>
                        <p style="margin: 5px 0; color: #666; font-size: 14px;">
                            🏢 {job['company']}<br>
                            📍 {job.get('location', 'Remote')}<br>
                            ⭐ {job.get('experience_level', 'Various levels')}
                        </p>
                    </div>
                    <div style="text-align: right;">
                        <div style="background: {match_color}; color: white; padding: 8px 12px; border-radius: 20px; font-weight: bold; margin-bottom: 5px;">
                            {job['match_percentage']}% Match
                        </div>
                        <div style="background: {ats_color}; color: white; padding: 4px 8px; border-radius: 12px; font-size: 12px;">
                            ATS: {job['ats_score']}/100
                        </div>
                    </div>
                </div>
                
                <p style="color: #555; font-size: 14px; line-height: 1.4;">
                    {job.get('description', '')[:200]}...
                </p>
                
                {missing_skills_html}
            </div>
            """
        
        return f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 650px; margin: 0 auto; background-color: #f5f7fa;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 25px; text-align: center;">
                <h1 style="color: white; margin: 0; font-size: 28px;">🎯 New Job Matches Found!</h1>
                <p style="color: #e8f0fe; margin: 10px 0 0 0;">AI Job Matcher found {len(job_matches)} opportunities for you</p>
            </div>
            
            <div style="padding: 30px; background-color: #f8f9ff;">
                <h2 style="color: #333;">Hi {user_name},</h2>
                
                <p style="color: #555; line-height: 1.6;">
                    Great news! Our AI has analyzed your resume and found <strong>{len(job_matches)} job opportunities</strong> that match your skills. Here are your top matches:
                </p>
                
                <div style="background: #e8f4fd; padding: 15px; border-radius: 8px; margin: 20px 0;">
                    <h4 style="margin: 0 0 10px 0; color: #1565c0;">📊 Your Skills Profile:</h4>
                    <div style="color: #333;">
                        {', '.join(user_skills[:10])}
                        {' and more...' if len(user_skills) > 10 else ''}
                    </div>
                </div>
                
                <h3 style="color: #333; margin: 30px 0 15px 0;">🏆 Top Job Matches:</h3>
                {job_cards_html}
                
                <div style="text-align: center; margin: 40px 0;">
                    <a href="https://your-app-url.com/recommend" style="background: #667eea; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; display: inline-block; font-weight: bold;">
                        View All {len(job_matches)} Matches
                    </a>
                </div>
                
                <div style="background: #fff3cd; padding: 15px; border-radius: 8px; border-left: 4px solid #ffc107;">
                    <h4 style="margin: 0 0 10px 0; color: #856404;">💡 Pro Tip:</h4>
                    <p style="margin: 0; color: #856404; font-size: 14px;">
                        Keep your resume updated with new skills and projects to get even better matches!
                    </p>
                </div>
            </div>
            
            <div style="background: #f0f0f0; padding: 20px; text-align: center; font-size: 12px; color: #666;">
                <p>You're receiving this because you subscribed to AI Job Matcher notifications.</p>
                <p><a href="https://your-app-url.com/unsubscribe" style="color: #667eea;">Unsubscribe</a> | <a href="https://your-app-url.com/settings" style="color: #667eea;">Manage Preferences</a></p>
            </div>
        </body>
        </html>
        """
    
    def _generate_job_match_text(self, user_name: str, job_matches: List[Dict], user_skills: List[str]) -> str:
        """Generate plain text content for job match notification."""
        
        job_text = ""
        for i, job in enumerate(job_matches[:3], 1):
            missing_text = f"\n   Skills to develop: {', '.join(job['missing_skills'][:5])}" if job['missing_skills'] else ""
            
            job_text += f"""
{i}. {job['title']} at {job['company']}
   Match: {job['match_percentage']}% | ATS Score: {job['ats_score']}/100
   Location: {job.get('location', 'Remote')}
   Level: {job.get('experience_level', 'Various levels')}
   {job.get('description', '')[:150]}...{missing_text}

"""
        
        return f"""
AI Job Matcher - New Opportunities Found!

Hi {user_name},

Great news! Our AI found {len(job_matches)} job opportunities that match your skills.

Your Skills: {', '.join(user_skills[:10])}{'...' if len(user_skills) > 10 else ''}

TOP MATCHES:
{job_text}

View all {len(job_matches)} matches: https://your-app-url.com/recommend

Keep your resume updated for even better matches!

---
You can unsubscribe or manage preferences at: https://your-app-url.com/settings
        """