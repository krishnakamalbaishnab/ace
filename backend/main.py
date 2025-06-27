from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from datetime import datetime
import json

app = FastAPI(
    title="ACE Study Abroad Consultancy API",
    description="Backend API for ACE Study Abroad Consultancy website",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class EnquiryForm(BaseModel):
    user_name: str
    user_email: EmailStr
    current_education: Optional[str] = None
    target_country: str
    preferred_intakes: Optional[str] = None
    message: str

class ContactForm(BaseModel):
    name: str
    email: EmailStr
    subject: str
    message: str

# Configuration
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "help.aceassignment@gmail.com")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "help.aceassignment@gmail.com")

# Data storage (in production, use a proper database)
ENQUIRIES_FILE = "enquiries.json"

def save_enquiry(enquiry_data: dict):
    """Save enquiry to JSON file (in production, use a database)"""
    try:
        enquiries = []
        if os.path.exists(ENQUIRIES_FILE):
            with open(ENQUIRIES_FILE, 'r') as f:
                enquiries = json.load(f)
        
        enquiry_data['timestamp'] = datetime.now().isoformat()
        enquiry_data['id'] = len(enquiries) + 1
        enquiries.append(enquiry_data)
        
        with open(ENQUIRIES_FILE, 'w') as f:
            json.dump(enquiries, f, indent=2)
            
    except Exception as e:
        print(f"Error saving enquiry: {e}")

def send_email(to_email: str, subject: str, body: str, is_html: bool = False):
    """Send email using SMTP"""
    try:
        msg = MIMEMultipart()
        msg['From'] = SMTP_USERNAME
        msg['To'] = to_email
        msg['Subject'] = subject
        
        if is_html:
            msg.attach(MIMEText(body, 'html'))
        else:
            msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def send_admin_notification(enquiry: EnquiryForm):
    """Send notification email to admin"""
    subject = f"New Study Abroad Enquiry from {enquiry.user_name}"
    
    body = f"""
    <h2>New Study Abroad Enquiry</h2>
    <p><strong>Name:</strong> {enquiry.user_name}</p>
    <p><strong>Email:</strong> {enquiry.user_email}</p>
    <p><strong>Current Education:</strong> {enquiry.current_education or 'Not specified'}</p>
    <p><strong>Target Country:</strong> {enquiry.target_country}</p>
    <p><strong>Preferred Intakes:</strong> {enquiry.preferred_intakes or 'Not specified'}</p>
    <p><strong>Message:</strong></p>
    <p>{enquiry.message}</p>
    <hr>
    <p><em>Received on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</em></p>
    """
    
    send_email(ADMIN_EMAIL, subject, body, is_html=True)

def send_auto_reply(enquiry: EnquiryForm):
    """Send auto-reply email to student"""
    subject = "Thank you for contacting ACE Study Abroad Consultancy"
    
    body = f"""
    <h2>Thank you for your enquiry!</h2>
    <p>Dear {enquiry.user_name},</p>
    <p>Thank you for contacting ACE Study Abroad Consultancy. We have received your enquiry about studying in {enquiry.target_country}.</p>
    <p>Our team will review your requirements and get back to you within 24 hours with personalized guidance and next steps.</p>
    <h3>What happens next?</h3>
    <ul>
        <li>We'll analyze your profile and requirements</li>
        <li>Provide university recommendations</li>
        <li>Outline the application process</li>
        <li>Answer any questions you may have</li>
    </ul>
    <p>In the meantime, you can:</p>
    <ul>
        <li>Check out our <a href="#countries">study destinations</a></li>
        <li>Explore our <a href="#services">services</a></li>
        <li>Review our <a href="#pricing">pricing plans</a></li>
    </ul>
    <p>If you have any urgent questions, feel free to reach out to us directly.</p>
    <p>Best regards,<br>The ACE Team</p>
    <hr>
    <p><small>This is an automated response. Please do not reply to this email.</small></p>
    """
    
    send_email(enquiry.user_email, subject, body, is_html=True)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "ACE Study Abroad Consultancy API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/api/enquiry")
async def submit_enquiry(enquiry: EnquiryForm, background_tasks: BackgroundTasks):
    """Submit a new study abroad enquiry"""
    try:
        # Save enquiry to storage
        background_tasks.add_task(save_enquiry, enquiry.dict())
        
        # Send admin notification
        background_tasks.add_task(send_admin_notification, enquiry)
        
        # Send auto-reply to student
        background_tasks.add_task(send_auto_reply, enquiry)
        
        return {
            "success": True,
            "message": "Enquiry submitted successfully. We'll get back to you within 24 hours.",
            "enquiry_id": datetime.now().strftime("%Y%m%d%H%M%S")
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing enquiry: {str(e)}")

@app.post("/api/contact")
async def submit_contact(contact: ContactForm, background_tasks: BackgroundTasks):
    """Submit a general contact form"""
    try:
        # Send admin notification
        subject = f"New Contact Form Submission: {contact.subject}"
        body = f"""
        <h2>New Contact Form Submission</h2>
        <p><strong>Name:</strong> {contact.name}</p>
        <p><strong>Email:</strong> {contact.email}</p>
        <p><strong>Subject:</strong> {contact.subject}</p>
        <p><strong>Message:</strong></p>
        <p>{contact.message}</p>
        """
        
        background_tasks.add_task(send_email, ADMIN_EMAIL, subject, body, True)
        
        return {
            "success": True,
            "message": "Message sent successfully. We'll respond soon."
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending message: {str(e)}")

@app.get("/api/enquiries")
async def get_enquiries():
    """Get all enquiries (admin only - in production, add authentication)"""
    try:
        if os.path.exists(ENQUIRIES_FILE):
            with open(ENQUIRIES_FILE, 'r') as f:
                enquiries = json.load(f)
            return {"enquiries": enquiries}
        else:
            return {"enquiries": []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving enquiries: {str(e)}")

@app.get("/api/countries")
async def get_countries():
    """Get available study countries"""
    countries = [
        {
            "code": "uk",
            "name": "United Kingdom",
            "flag": "🇬🇧",
            "description": "World-class universities, rich history, and diverse culture",
            "top_universities": ["Oxford", "Cambridge", "LSE"],
            "duration": "1-4 years",
            "work_rights": "20 hrs/week",
            "tuition_fee_range": "£10,000 - £35,000/year"
        },
        {
            "code": "germany",
            "name": "Germany",
            "flag": "🇩🇪",
            "description": "Free education, strong economy, and innovation hub",
            "top_universities": ["TU Munich", "Heidelberg"],
            "duration": "2-4 years",
            "work_rights": "120 days/year",
            "tuition_fee_range": "€0 - €1,500/year"
        },
        {
            "code": "usa",
            "name": "United States",
            "flag": "🇺🇸",
            "description": "Innovation capital, diverse programs, and career opportunities",
            "top_universities": ["MIT", "Stanford", "Harvard"],
            "duration": "2-4 years",
            "work_rights": "20 hrs/week",
            "tuition_fee_range": "$20,000 - $60,000/year"
        },
        {
            "code": "canada",
            "name": "Canada",
            "flag": "🇨🇦",
            "description": "High quality of life, welcoming environment, and PR pathways",
            "top_universities": ["UofT", "McGill", "UBC"],
            "duration": "2-4 years",
            "work_rights": "20 hrs/week",
            "tuition_fee_range": "CAD 15,000 - 45,000/year"
        },
        {
            "code": "netherlands",
            "name": "Netherlands",
            "flag": "🇳🇱",
            "description": "English-taught programs, bike-friendly cities, and innovation",
            "top_universities": ["TU Delft", "UvA"],
            "duration": "1-3 years",
            "work_rights": "16 hrs/week",
            "tuition_fee_range": "€2,000 - €15,000/year"
        },
        {
            "code": "australia",
            "name": "Australia",
            "flag": "🇦🇺",
            "description": "Beautiful landscapes, quality education, and work opportunities",
            "top_universities": ["Melbourne", "Sydney"],
            "duration": "1-4 years",
            "work_rights": "40 hrs/fortnight",
            "tuition_fee_range": "AUD 20,000 - 50,000/year"
        },
        {
            "code": "ireland",
            "name": "Ireland",
            "flag": "🇮🇪",
            "description": "English-speaking, friendly culture, and EU opportunities",
            "top_universities": ["Trinity", "UCD", "Cork"],
            "duration": "1-4 years",
            "work_rights": "20 hrs/week",
            "tuition_fee_range": "€10,000 - €25,000/year"
        },
        {
            "code": "france",
            "name": "France",
            "flag": "🇫🇷",
            "description": "Rich culture, excellent cuisine, and renowned universities",
            "top_universities": ["Sorbonne", "Sciences Po"],
            "duration": "1-5 years",
            "work_rights": "20 hrs/week",
            "tuition_fee_range": "€3,000 - €15,000/year"
        },
        {
            "code": "sweden",
            "name": "Sweden",
            "flag": "🇸🇪",
            "description": "Innovation hub, high quality of life, and sustainability focus",
            "top_universities": ["KTH", "Lund", "Stockholm"],
            "duration": "1-3 years",
            "work_rights": "Part-time allowed",
            "tuition_fee_range": "SEK 80,000 - 140,000/year"
        },
        {
            "code": "new_zealand",
            "name": "New Zealand",
            "flag": "🇳🇿",
            "description": "Stunning nature, peaceful environment, and quality education",
            "top_universities": ["Auckland", "Otago"],
            "duration": "1-4 years",
            "work_rights": "20 hrs/week",
            "tuition_fee_range": "NZD 22,000 - 35,000/year"
        },
        {
            "code": "finland",
            "name": "Finland",
            "flag": "🇫🇮",
            "description": "Top education system, innovation, and beautiful nature",
            "top_universities": ["Helsinki", "Aalto"],
            "duration": "2-5 years",
            "work_rights": "25 hrs/week",
            "tuition_fee_range": "€8,000 - €18,000/year"
        },
        {
            "code": "singapore",
            "name": "Singapore",
            "flag": "🇸🇬",
            "description": "Asia's education hub, multicultural, and business gateway",
            "top_universities": ["NUS", "NTU", "SMU"],
            "duration": "1-4 years",
            "work_rights": "16 hrs/week",
            "tuition_fee_range": "SGD 30,000 - 50,000/year"
        },
        {
            "code": "japan",
            "name": "Japan",
            "flag": "🇯🇵",
            "description": "Technology leader, rich culture, and unique experiences",
            "top_universities": ["Tokyo", "Kyoto", "Waseda"],
            "duration": "2-4 years",
            "work_rights": "28 hrs/week",
            "tuition_fee_range": "¥500,000 - ¥1,500,000/year"
        },
        {
            "code": "south_korea",
            "name": "South Korea",
            "flag": "🇰🇷",
            "description": "K-culture, technology innovation, and scholarships",
            "top_universities": ["SNU", "KAIST", "Yonsei"],
            "duration": "2-4 years",
            "work_rights": "20 hrs/week",
            "tuition_fee_range": "₩4,000,000 - ₩12,000,000/year"
        },
        {
            "code": "italy",
            "name": "Italy",
            "flag": "🇮🇹",
            "description": "Art, culture, history, and affordable European education",
            "top_universities": ["Bocconi", "Bologna"],
            "duration": "1-5 years",
            "work_rights": "20 hrs/week",
            "tuition_fee_range": "€1,000 - €4,000/year"
        }
    ]
    return {"countries": countries}

@app.get("/api/services")
async def get_services():
    """Get available services"""
    services = [
        {
            "id": "university_shortlisting",
            "name": "University Shortlisting",
            "icon": "fas fa-university",
            "description": "Personalized university recommendations based on your profile, budget, and career goals.",
            "features": [
                "Program research & analysis",
                "Entry requirements check",
                "Application deadlines tracking"
            ]
        },
        {
            "id": "application_support",
            "name": "Application Support",
            "icon": "fas fa-file-alt",
            "description": "Expert guidance for SOP, Resume, LOR, and all application documents.",
            "features": [
                "Statement of Purpose writing",
                "Resume/CV optimization",
                "Letter of Recommendation guidance"
            ]
        },
        {
            "id": "assignment_mentoring",
            "name": "Assignment & Project Mentoring",
            "icon": "fas fa-graduation-cap",
            "description": "Academic support to help you excel in your studies abroad.",
            "features": [
                "Assignment writing assistance",
                "Project guidance & mentoring",
                "Research methodology support"
            ]
        },
        {
            "id": "job_support",
            "name": "Part-time Job Support",
            "icon": "fas fa-briefcase",
            "description": "Help you find suitable part-time work opportunities while studying.",
            "features": [
                "Job search strategies",
                "CV preparation for local market",
                "Interview preparation"
            ]
        },
        {
            "id": "accommodation",
            "name": "Accommodation Help",
            "icon": "fas fa-home",
            "description": "Assistance in finding safe and affordable accommodation options.",
            "features": [
                "Student housing options",
                "Rental guidance & contracts",
                "Location recommendations"
            ]
        },
        {
            "id": "visa_support",
            "name": "Visa & Pre-departure",
            "icon": "fas fa-plane",
            "description": "Complete visa application support and pre-departure guidance.",
            "features": [
                "Visa application assistance",
                "Document preparation",
                "Pre-departure checklist"
            ]
        }
    ]
    return {"services": services}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 