from fastapi import FastAPI, APIRouter, HTTPException, Depends, UploadFile, File, Response, Request, Form
from fastapi.responses import JSONResponse, StreamingResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone, timedelta
import bcrypt
import jwt
import httpx
import json
import asyncio
import base64
import io

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# JWT Configuration
JWT_SECRET = os.environ.get('JWT_SECRET_KEY', 'default_secret_key')
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 168  # 7 days

# LLM Configuration
# EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY')

EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY')
openai_client = AsyncOpenAI(api_key=EMERGENT_LLM_KEY) if EMERGENT_LLM_KEY else None

# Admin credentials for teacher approval
ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'rahulyadavjnvshravasti669@gmail.com')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'Dakshana@123')

app = FastAPI()
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============== MODELS ==============

class UserBase(BaseModel):
    email: EmailStr
    name: str
    role: str  # 'student' or 'teacher' or 'admin'

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(UserBase):
    model_config = ConfigDict(extra="ignore")
    user_id: str
    picture: Optional[str] = None
    created_at: datetime
    is_approved: bool = True

class UserResponse(BaseModel):
    user_id: str
    email: str
    name: str
    role: str
    picture: Optional[str] = None
    is_approved: bool = True

class TokenResponse(BaseModel):
    token: str
    user: UserResponse

# Paper Models
class Paper(BaseModel):
    model_config = ConfigDict(extra="ignore")
    paper_id: str
    title: str
    subject: str
    exam_type: str
    sub_type: Optional[str] = None
    class_level: Optional[str] = None
    year: Optional[str] = None
    questions: List[Dict[str, Any]]
    created_by: str
    created_at: datetime
    language: str = "English"

class PaperCreate(BaseModel):
    title: str
    subject: str
    exam_type: str
    sub_type: Optional[str] = None
    class_level: Optional[str] = None
    year: Optional[str] = None
    questions: List[Dict[str, Any]]
    language: str = "English"

# Doubt Models
class Doubt(BaseModel):
    model_config = ConfigDict(extra="ignore")
    doubt_id: str
    student_id: str
    student_name: str
    subject: str
    question_text: str
    question_image: Optional[str] = None
    status: str = "pending"
    answer_text: Optional[str] = None
    answer_image: Optional[str] = None
    answered_by: Optional[str] = None
    created_at: datetime
    answered_at: Optional[datetime] = None

class DoubtCreate(BaseModel):
    subject: str
    question_text: str
    question_image: Optional[str] = None

class DoubtAnswer(BaseModel):
    answer_text: Optional[str] = None
    answer_image: Optional[str] = None

# Test Models
class TestResult(BaseModel):
    model_config = ConfigDict(extra="ignore")
    result_id: str
    student_id: str
    paper_id: str
    paper_title: str
    exam_type: str
    subject: str
    total_questions: int
    correct_answers: int
    wrong_answers: int
    unattempted: int
    score: float
    accuracy: float
    time_taken: int
    subject_wise: Dict[str, Dict[str, int]]
    created_at: datetime

class TestSubmission(BaseModel):
    paper_id: str
    answers: Dict[str, str]
    time_taken: int

# AI Paper Generation Models
class PaperGenerationRequest(BaseModel):
    num_questions: int
    subject: str
    difficulty: str
    purpose: str
    sub_type: Optional[str] = None
    class_level: Optional[str] = None
    language: str = "English"
    reference_content: Optional[str] = None

# Generated Paper Save Model
class SaveGeneratedPaper(BaseModel):
    title: str
    subject: str
    exam_type: str
    sub_type: Optional[str] = None
    class_level: Optional[str] = None
    year: Optional[str] = None
    questions: List[Dict[str, Any]]
    language: str = "English"

# Teacher Approval Model
class TeacherApproval(BaseModel):
    user_id: str
    approve: bool

# Notification Model
class Notification(BaseModel):
    notification_id: str
    user_id: str
    message: str
    type: str  # 'doubt_answered', 'teacher_approved', etc.
    is_read: bool = False
    created_at: datetime
    related_id: Optional[str] = None

# ============== AUTH HELPERS ==============

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())

def create_token(user_id: str) -> str:
    payload = {
        "user_id": user_id,
        "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

async def get_current_user(request: Request) -> dict:
    token = request.cookies.get("session_token")
    
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
    
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    session = await db.user_sessions.find_one({"session_token": token}, {"_id": 0})
    if session:
        expires_at = session.get("expires_at")
        if isinstance(expires_at, str):
            expires_at = datetime.fromisoformat(expires_at)
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if expires_at < datetime.now(timezone.utc):
            raise HTTPException(status_code=401, detail="Session expired")
        
        user = await db.users.find_one({"user_id": session["user_id"]}, {"_id": 0})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user = await db.users.find_one({"user_id": payload["user_id"]}, {"_id": 0})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_admin_user(request: Request) -> dict:
    user = await get_current_user(request)
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user

# ============== AUTH ENDPOINTS ==============

@api_router.post("/auth/register")
async def register(user_data: UserCreate):
    existing = await db.users.find_one({"email": user_data.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user_id = f"user_{uuid.uuid4().hex[:12]}"
    hashed_password = hash_password(user_data.password)
    
    # Teachers need approval, students are auto-approved
    is_approved = user_data.role != "teacher"
    
    user_doc = {
        "user_id": user_id,
        "email": user_data.email,
        "name": user_data.name,
        "role": user_data.role,
        "password": hashed_password,
        "picture": None,
        "is_approved": is_approved,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.users.insert_one(user_doc)
    token = create_token(user_id)
    
    return {
        "token": token,
        "user": {
            "user_id": user_id,
            "email": user_data.email,
            "name": user_data.name,
            "role": user_data.role,
            "picture": None,
            "is_approved": is_approved
        }
    }

@api_router.post("/auth/login")
async def login(credentials: UserLogin):
    user = await db.users.find_one({"email": credentials.email}, {"_id": 0})
    if not user or not verify_password(credentials.password, user.get("password", "")):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_token(user["user_id"])
    
    return {
        "token": token,
        "user": {
            "user_id": user["user_id"],
            "email": user["email"],
            "name": user["name"],
            "role": user["role"],
            "picture": user.get("picture"),
            "is_approved": user.get("is_approved", True)
        }
    }

@api_router.post("/auth/admin-login")
async def admin_login(credentials: UserLogin):
    """Admin login endpoint"""
    if credentials.email == ADMIN_EMAIL and credentials.password == ADMIN_PASSWORD:
        # Check if admin exists
        admin = await db.users.find_one({"email": ADMIN_EMAIL}, {"_id": 0})
        if not admin:
            # Create admin user
            admin_id = f"admin_{uuid.uuid4().hex[:12]}"
            admin_doc = {
                "user_id": admin_id,
                "email": ADMIN_EMAIL,
                "name": "Admin",
                "role": "admin",
                "password": hash_password(ADMIN_PASSWORD),
                "picture": None,
                "is_approved": True,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            await db.users.insert_one(admin_doc)
            admin = admin_doc
        
        token = create_token(admin["user_id"])
        return {
            "token": token,
            "user": {
                "user_id": admin["user_id"],
                "email": admin["email"],
                "name": admin["name"],
                "role": admin["role"],
                "picture": admin.get("picture"),
                "is_approved": True
            }
        }
    raise HTTPException(status_code=401, detail="Invalid admin credentials")

@api_router.post("/auth/session")
async def process_google_session(request: Request, response: Response):
    body = await request.json()
    session_id = body.get("session_id")
    role = body.get("role", "student")
    
    if not session_id:
        raise HTTPException(status_code=400, detail="session_id required")
    
    async with httpx.AsyncClient() as client:
        auth_response = await client.get(
            "https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data",
            headers={"X-Session-ID": session_id}
        )
        if auth_response.status_code != 200:
            raise HTTPException(status_code=401, detail="Invalid session")
        
        user_data = auth_response.json()
    
    existing_user = await db.users.find_one({"email": user_data["email"]}, {"_id": 0})
    
    if existing_user:
        user_id = existing_user["user_id"]
        role = existing_user["role"]
        is_approved = existing_user.get("is_approved", True)
    else:
        user_id = f"user_{uuid.uuid4().hex[:12]}"
        is_approved = role != "teacher"
        new_user = {
            "user_id": user_id,
            "email": user_data["email"],
            "name": user_data["name"],
            "role": role,
            "picture": user_data.get("picture"),
            "password": None,
            "is_approved": is_approved,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.users.insert_one(new_user)
    
    session_token = user_data["session_token"]
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)
    
    await db.user_sessions.update_one(
        {"user_id": user_id},
        {
            "$set": {
                "user_id": user_id,
                "session_token": session_token,
                "expires_at": expires_at.isoformat(),
                "created_at": datetime.now(timezone.utc).isoformat()
            }
        },
        upsert=True
    )
    
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        secure=True,
        samesite="none",
        path="/",
        max_age=7 * 24 * 60 * 60
    )
    
    return {
        "user_id": user_id,
        "email": user_data["email"],
        "name": user_data["name"],
        "role": role,
        "picture": user_data.get("picture"),
        "is_approved": is_approved
    }

@api_router.get("/auth/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    return {
        "user_id": current_user["user_id"],
        "email": current_user["email"],
        "name": current_user["name"],
        "role": current_user["role"],
        "picture": current_user.get("picture"),
        "is_approved": current_user.get("is_approved", True)
    }

@api_router.post("/auth/logout")
async def logout(request: Request, response: Response):
    token = request.cookies.get("session_token")
    if token:
        await db.user_sessions.delete_one({"session_token": token})
    response.delete_cookie(key="session_token", path="/")
    return {"message": "Logged out successfully"}

# ============== ADMIN ENDPOINTS ==============

@api_router.get("/admin/pending-teachers")
async def get_pending_teachers(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    teachers = await db.users.find(
        {"role": "teacher", "is_approved": False},
        {"_id": 0, "password": 0}
    ).to_list(100)
    return teachers

@api_router.get("/admin/all-teachers")
async def get_all_teachers(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    teachers = await db.users.find(
        {"role": "teacher"},
        {"_id": 0, "password": 0}
    ).to_list(100)
    return teachers

@api_router.post("/admin/approve-teacher")
async def approve_teacher(approval: TeacherApproval, current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    result = await db.users.update_one(
        {"user_id": approval.user_id, "role": "teacher"},
        {"$set": {"is_approved": approval.approve}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Teacher not found")
    
    # Create notification for teacher
    notification_id = f"notif_{uuid.uuid4().hex[:12]}"
    notification_doc = {
        "notification_id": notification_id,
        "user_id": approval.user_id,
        "message": "Your teacher account has been approved! You can now access the dashboard." if approval.approve else "Your teacher account approval has been revoked.",
        "type": "teacher_approved" if approval.approve else "teacher_revoked",
        "is_read": False,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "related_id": None
    }
    await db.notifications.insert_one(notification_doc)
    
    return {"message": f"Teacher {'approved' if approval.approve else 'disapproved'} successfully"}

# ============== NOTIFICATIONS ENDPOINTS ==============

@api_router.get("/notifications")
async def get_notifications(current_user: dict = Depends(get_current_user)):
    notifications = await db.notifications.find(
        {"user_id": current_user["user_id"]},
        {"_id": 0}
    ).sort("created_at", -1).to_list(50)
    return notifications

@api_router.get("/notifications/unread-count")
async def get_unread_count(current_user: dict = Depends(get_current_user)):
    count = await db.notifications.count_documents({
        "user_id": current_user["user_id"],
        "is_read": False
    })
    return {"count": count}

@api_router.put("/notifications/{notification_id}/read")
async def mark_notification_read(notification_id: str, current_user: dict = Depends(get_current_user)):
    await db.notifications.update_one(
        {"notification_id": notification_id, "user_id": current_user["user_id"]},
        {"$set": {"is_read": True}}
    )
    return {"message": "Notification marked as read"}

@api_router.put("/notifications/mark-all-read")
async def mark_all_read(current_user: dict = Depends(get_current_user)):
    await db.notifications.update_many(
        {"user_id": current_user["user_id"]},
        {"$set": {"is_read": True}}
    )
    return {"message": "All notifications marked as read"}

# ============== PAPERS ENDPOINTS ==============

@api_router.get("/papers", response_model=List[Dict[str, Any]])
async def get_papers(
    subject: Optional[str] = None,
    exam_type: Optional[str] = None,
    class_level: Optional[str] = None,
    year: Optional[str] = None
):
    query = {}
    if subject:
        query["subject"] = subject
    if exam_type:
        query["exam_type"] = exam_type
    if class_level:
        query["class_level"] = class_level
    if year:
        query["year"] = year
    
    papers = await db.papers.find(query, {"_id": 0}).to_list(100)
    return papers

@api_router.get("/papers/{paper_id}")
async def get_paper(paper_id: str):
    paper = await db.papers.find_one({"paper_id": paper_id}, {"_id": 0})
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    return paper

@api_router.post("/papers", response_model=Dict[str, Any])
async def create_paper(paper_data: PaperCreate, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can create papers")
    
    if not current_user.get("is_approved", True):
        raise HTTPException(status_code=403, detail="Your account is pending approval")
    
    paper_id = f"paper_{uuid.uuid4().hex[:12]}"
    paper_doc = {
        "paper_id": paper_id,
        "title": paper_data.title,
        "subject": paper_data.subject,
        "exam_type": paper_data.exam_type,
        "sub_type": paper_data.sub_type,
        "class_level": paper_data.class_level,
        "year": paper_data.year,
        "questions": paper_data.questions,
        "language": paper_data.language,
        "created_by": current_user["user_id"],
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.papers.insert_one(paper_doc)
    return {k: v for k, v in paper_doc.items() if k != "_id"}

@api_router.get("/papers/{paper_id}/download")
async def download_paper_pdf(paper_id: str):
    paper = await db.papers.find_one({"paper_id": paper_id}, {"_id": 0})
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    
    # Generate PDF content
    pdf_content = generate_paper_pdf(paper)
    
    return StreamingResponse(
        io.BytesIO(pdf_content),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={paper['title'].replace(' ', '_')}.pdf"}
    )

def generate_paper_pdf(paper: dict) -> bytes:
    """Generate a simple text-based PDF-like content"""
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import inch
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.enums import TA_LEFT, TA_CENTER
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = styles['Heading1']
    title_style.alignment = TA_CENTER
    story.append(Paragraph(paper['title'], title_style))
    story.append(Spacer(1, 12))
    
    # Metadata
    meta_style = styles['Normal']
    story.append(Paragraph(f"<b>Subject:</b> {paper['subject']}", meta_style))
    story.append(Paragraph(f"<b>Exam Type:</b> {paper['exam_type']}", meta_style))
    if paper.get('year'):
        story.append(Paragraph(f"<b>Year:</b> {paper['year']}", meta_style))
    story.append(Spacer(1, 24))
    
    # Questions
    question_style = styles['Normal']
    for i, q in enumerate(paper['questions'], 1):
        story.append(Paragraph(f"<b>Q{i}.</b> {q['question_text']}", question_style))
        story.append(Spacer(1, 6))
        for opt_key, opt_val in q['options'].items():
            story.append(Paragraph(f"    ({opt_key}) {opt_val}", question_style))
        story.append(Spacer(1, 12))
    
    # Answer Key
    story.append(Spacer(1, 24))
    story.append(Paragraph("<b>Answer Key:</b>", styles['Heading2']))
    story.append(Spacer(1, 12))
    answers = ", ".join([f"Q{i+1}: {q['correct_answer']}" for i, q in enumerate(paper['questions'])])
    story.append(Paragraph(answers, question_style))
    
    doc.build(story)
    buffer.seek(0)
    return buffer.read()

# ============== DOUBTS ENDPOINTS ==============

@api_router.get("/doubts", response_model=List[Dict[str, Any]])
async def get_doubts(
    status: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    query = {}
    if current_user["role"] == "student":
        query["student_id"] = current_user["user_id"]
    if status:
        query["status"] = status
    
    doubts = await db.doubts.find(query, {"_id": 0}).sort("created_at", -1).to_list(100)
    return doubts

@api_router.post("/doubts", response_model=Dict[str, Any])
async def create_doubt(doubt_data: DoubtCreate, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "student":
        raise HTTPException(status_code=403, detail="Only students can create doubts")
    
    doubt_id = f"doubt_{uuid.uuid4().hex[:12]}"
    doubt_doc = {
        "doubt_id": doubt_id,
        "student_id": current_user["user_id"],
        "student_name": current_user["name"],
        "subject": doubt_data.subject,
        "question_text": doubt_data.question_text,
        "question_image": doubt_data.question_image,
        "status": "pending",
        "answer_text": None,
        "answer_image": None,
        "answered_by": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "answered_at": None
    }
    
    await db.doubts.insert_one(doubt_doc)
    return {k: v for k, v in doubt_doc.items() if k != "_id"}

@api_router.put("/doubts/{doubt_id}/answer")
async def answer_doubt(doubt_id: str, answer: DoubtAnswer, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can answer doubts")
    
    if not current_user.get("is_approved", True):
        raise HTTPException(status_code=403, detail="Your account is pending approval")
    
    doubt = await db.doubts.find_one({"doubt_id": doubt_id})
    if not doubt:
        raise HTTPException(status_code=404, detail="Doubt not found")
    
    update_data = {
        "status": "answered",
        "answer_text": answer.answer_text,
        "answer_image": answer.answer_image,
        "answered_by": current_user["user_id"],
        "answered_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.doubts.update_one({"doubt_id": doubt_id}, {"$set": update_data})
    
    # Create notification for student
    notification_id = f"notif_{uuid.uuid4().hex[:12]}"
    notification_doc = {
        "notification_id": notification_id,
        "user_id": doubt["student_id"],
        "message": f"Your doubt in {doubt['subject']} has been answered!",
        "type": "doubt_answered",
        "is_read": False,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "related_id": doubt_id
    }
    await db.notifications.insert_one(notification_doc)
    
    return {"message": "Doubt answered successfully"}

@api_router.post("/doubts/upload-image")
async def upload_doubt_image(
    image: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """Upload image for doubt question or answer"""
    contents = await image.read()
    base64_image = base64.b64encode(contents).decode('utf-8')
    content_type = image.content_type or 'image/png'
    data_url = f"data:{content_type};base64,{base64_image}"
    return {"image_url": data_url}

# ============== TESTS ENDPOINTS ==============

@api_router.post("/tests/submit", response_model=Dict[str, Any])
async def submit_test(submission: TestSubmission, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "student":
        raise HTTPException(status_code=403, detail="Only students can submit tests")
    
    paper = await db.papers.find_one({"paper_id": submission.paper_id}, {"_id": 0})
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    
    total_questions = len(paper["questions"])
    correct = 0
    wrong = 0
    unattempted = 0
    subject_wise = {}
    
    for q in paper["questions"]:
        q_id = q["question_id"]
        subject = q.get("subject", paper["subject"])
        
        if subject not in subject_wise:
            subject_wise[subject] = {"total": 0, "correct": 0, "wrong": 0}
        subject_wise[subject]["total"] += 1
        
        if q_id not in submission.answers or not submission.answers[q_id]:
            unattempted += 1
        elif submission.answers[q_id] == q["correct_answer"]:
            correct += 1
            subject_wise[subject]["correct"] += 1
        else:
            wrong += 1
            subject_wise[subject]["wrong"] += 1
    
    score = (correct * 4) - (wrong * 1)
    accuracy = (correct / (correct + wrong) * 100) if (correct + wrong) > 0 else 0
    
    result_id = f"result_{uuid.uuid4().hex[:12]}"
    result_doc = {
        "result_id": result_id,
        "student_id": current_user["user_id"],
        "paper_id": submission.paper_id,
        "paper_title": paper["title"],
        "exam_type": paper["exam_type"],
        "subject": paper["subject"],
        "total_questions": total_questions,
        "correct_answers": correct,
        "wrong_answers": wrong,
        "unattempted": unattempted,
        "score": score,
        "accuracy": round(accuracy, 2),
        "time_taken": submission.time_taken,
        "subject_wise": subject_wise,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.test_results.insert_one(result_doc)
    return {k: v for k, v in result_doc.items() if k != "_id"}

@api_router.get("/tests/results", response_model=List[Dict[str, Any]])
async def get_test_results(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "student":
        raise HTTPException(status_code=403, detail="Only students can view their results")
    
    results = await db.test_results.find(
        {"student_id": current_user["user_id"]},
        {"_id": 0}
    ).sort("created_at", -1).to_list(100)
    return results

@api_router.get("/tests/results/{result_id}")
async def get_test_result(result_id: str, current_user: dict = Depends(get_current_user)):
    result = await db.test_results.find_one({"result_id": result_id}, {"_id": 0})
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")
    if current_user["role"] == "student" and result["student_id"] != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    return result

# ============== PROGRESS ENDPOINTS ==============

@api_router.get("/progress")
async def get_progress(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "student":
        raise HTTPException(status_code=403, detail="Only students can view progress")
    
    results = await db.test_results.find(
        {"student_id": current_user["user_id"]},
        {"_id": 0}
    ).to_list(1000)
    
    if not results:
        return {
            "total_tests": 0,
            "average_score": 0,
            "average_accuracy": 0,
            "subject_performance": {},
            "recent_results": [],
            "improvement_trend": []
        }
    
    total_tests = len(results)
    avg_score = sum(r["score"] for r in results) / total_tests
    avg_accuracy = sum(r["accuracy"] for r in results) / total_tests
    
    subject_performance = {}
    for r in results:
        for subject, data in r.get("subject_wise", {}).items():
            if subject not in subject_performance:
                subject_performance[subject] = {"total": 0, "correct": 0, "tests": 0}
            subject_performance[subject]["total"] += data["total"]
            subject_performance[subject]["correct"] += data["correct"]
            subject_performance[subject]["tests"] += 1
    
    for subject in subject_performance:
        total = subject_performance[subject]["total"]
        correct = subject_performance[subject]["correct"]
        subject_performance[subject]["accuracy"] = round((correct / total * 100) if total > 0 else 0, 2)
    
    recent_results = sorted(results, key=lambda x: x["created_at"], reverse=True)[:10]
    
    improvement_trend = [
        {"date": r["created_at"], "score": r["score"], "accuracy": r["accuracy"]}
        for r in sorted(results, key=lambda x: x["created_at"])[-10:]
    ]
    
    return {
        "total_tests": total_tests,
        "average_score": round(avg_score, 2),
        "average_accuracy": round(avg_accuracy, 2),
        "subject_performance": subject_performance,
        "recent_results": recent_results,
        "improvement_trend": improvement_trend
    }

# ============== AI PAPER GENERATION ==============

@api_router.post("/generate-paper")
async def generate_paper(
    request: PaperGenerationRequest,
    current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can generate papers")

    if not current_user.get("is_approved", True):
        raise HTTPException(status_code=403, detail="Your account is pending approval")

    if not EMERGENT_LLM_KEY:
        raise HTTPException(status_code=500, detail="OpenAI API key not configured")  

    try:
        client = AsyncOpenAI(api_key=EMERGENT_LLM_KEY)

        exam_context = request.purpose
        if request.sub_type:
            exam_context += f" ({request.sub_type})"
        if request.class_level:
            exam_context += f" for Class {request.class_level}"

        prompt = f"""
Generate {request.num_questions} multiple choice questions for {exam_context} exam.

Subject: {request.subject}
Difficulty: {request.difficulty}
Language: {request.language}

{f"Reference Content: {request.reference_content}" if request.reference_content else ""}

Return ONLY valid JSON in the following format:
{{
  "questions": [
    {{
      "question_id": "q1",
      "question_text": "Question text here",
      "subject": "{request.subject}",
      "options": {{
        "A": "Option A",
        "B": "Option B",
        "C": "Option C",
        "D": "Option D"
      }},
      "correct_answer": "A",
      "explanation": "Brief explanation",
      "difficulty": "{request.difficulty}"
    }}
  ]
}}

Important:
- Create unique, exam-quality questions
- Ensure correct answers are accurate
- Provide clear explanations
- Mix different topics within the subject
- Return ONLY valid JSON, no markdown or extra text
"""

        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert educational content creator. "
                        "Always return ONLY valid JSON. No markdown."
                    )
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
        )

        response_text = response.choices[0].message.content.strip()

        questions_data = json.loads(response_text)
        questions = questions_data.get("questions", [])

        for i, q in enumerate(questions):
            q.setdefault("question_id", f"q{i+1}")

        gen_paper_id = f"gen_{uuid.uuid4().hex[:12]}"
        gen_paper_doc = {
            "gen_paper_id": gen_paper_id,
            "teacher_id": current_user["user_id"],
            "num_questions": len(questions),
            "subject": request.subject,
            "difficulty": request.difficulty,
            "exam_type": request.purpose,
            "sub_type": request.sub_type,
            "class_level": request.class_level,
            "language": request.language,
            "questions": questions,
            "is_published": False,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        await db.generated_papers.insert_one(gen_paper_doc)

        return {
            "success": True,
            "gen_paper_id": gen_paper_id,
            "questions": questions,
            "metadata": {
                "num_questions": len(questions),
                "subject": request.subject,
                "difficulty": request.difficulty,
                "exam_type": request.purpose,
                "language": request.language,
            },
        }

    except json.JSONDecodeError as e:
        logger.error(f"JSON parse error: {e}")
        raise HTTPException(status_code=500, detail="Failed to parse generated questions")

    except Exception as e:
        logger.error(f"Paper generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============== VOICE TRANSCRIPTION ==============

@api_router.post("/transcribe")
async def transcribe_audio(
    audio: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    if not EMERGENT_LLM_KEY:
        raise HTTPException(status_code=500, detail="OpenAI API key not configured")

    try:
        client = AsyncOpenAI(api_key=EMERGENT_LLM_KEY)

        audio_bytes = await audio.read()

        transcription = await client.audio.transcriptions.create(
            file=(audio.filename or "audio.webm", audio_bytes),
            model="whisper-1",
            language="en",
        )

        return {"text": transcription.text}

    except Exception as e:
        logger.error(f"Transcription error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============== FILE UPLOAD FOR REFERENCE ==============

@api_router.post("/upload-reference")
async def upload_reference_file(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """Upload reference file (PDF/DOC) for paper generation"""
    if current_user["role"] != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can upload reference files")
    
    contents = await file.read()
    
    # For now, we'll extract text from the file
    # In production, you'd use proper PDF/DOC parsing libraries
    try:
        # Try to decode as text
        text_content = contents.decode('utf-8')
    except:
        # If binary (PDF/DOC), return base64 for storage
        text_content = f"[Binary file: {file.filename}]"
    
    return {
        "filename": file.filename,
        "content": text_content[:5000],  # Limit content size
        "message": "File uploaded successfully"
    }

# ============== SEED DATA ==============

@api_router.post("/seed")
async def seed_data():
    """Seed initial sample data for testing"""
    
    sample_papers = [
        {
            "paper_id": "paper_jee_mains_2024",
            "title": "JEE Mains 2024 - Physics",
            "subject": "Physics",
            "exam_type": "JEE",
            "sub_type": "JEE Mains",
            "class_level": None,
            "year": "2024",
            "language": "English",
            "questions": [
                {
                    "question_id": "q1",
                    "question_text": "A ball is thrown vertically upward with a velocity of 20 m/s. What is the maximum height reached?",
                    "subject": "Physics",
                    "options": {"A": "10 m", "B": "20 m", "C": "40 m", "D": "80 m"},
                    "correct_answer": "B",
                    "explanation": "Using v² = u² - 2gh, at max height v=0, so h = u²/2g = 400/20 = 20m",
                    "difficulty": "Medium"
                },
                {
                    "question_id": "q2",
                    "question_text": "The SI unit of electric field is:",
                    "subject": "Physics",
                    "options": {"A": "N/C", "B": "V/m", "C": "Both A and B", "D": "None"},
                    "correct_answer": "C",
                    "explanation": "Electric field can be expressed in both N/C and V/m as they are equivalent",
                    "difficulty": "Easy"
                },
                {
                    "question_id": "q3",
                    "question_text": "A capacitor of 4 μF is charged to 100 V. The energy stored is:",
                    "subject": "Physics",
                    "options": {"A": "0.02 J", "B": "0.04 J", "C": "0.2 J", "D": "2 J"},
                    "correct_answer": "A",
                    "explanation": "E = ½CV² = ½ × 4×10⁻⁶ × 10000 = 0.02 J",
                    "difficulty": "Medium"
                }
            ],
            "created_by": "system",
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "paper_id": "paper_neet_2024",
            "title": "NEET 2024 - Biology Mock",
            "subject": "Biology",
            "exam_type": "NEET",
            "sub_type": None,
            "class_level": None,
            "year": "2024",
            "language": "English",
            "questions": [
                {
                    "question_id": "q1",
                    "question_text": "Which organelle is known as the powerhouse of the cell?",
                    "subject": "Biology",
                    "options": {"A": "Nucleus", "B": "Mitochondria", "C": "Ribosome", "D": "Golgi body"},
                    "correct_answer": "B",
                    "explanation": "Mitochondria produce ATP through cellular respiration",
                    "difficulty": "Easy"
                },
                {
                    "question_id": "q2",
                    "question_text": "The process of DNA replication is:",
                    "subject": "Biology",
                    "options": {"A": "Conservative", "B": "Semi-conservative", "C": "Dispersive", "D": "Random"},
                    "correct_answer": "B",
                    "explanation": "DNA replication is semi-conservative as proved by Meselson and Stahl",
                    "difficulty": "Medium"
                }
            ],
            "created_by": "system",
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "paper_id": "paper_school_10_math",
            "title": "Class 10 Mathematics - Chapter Test",
            "subject": "Mathematics",
            "exam_type": "School",
            "sub_type": None,
            "class_level": "10",
            "year": "2024",
            "language": "English",
            "questions": [
                {
                    "question_id": "q1",
                    "question_text": "If the sum of zeros of p(x) = kx² + 2x + 3k is equal to their product, find k.",
                    "subject": "Mathematics",
                    "options": {"A": "1/3", "B": "-1/3", "C": "2/3", "D": "-2/3"},
                    "correct_answer": "C",
                    "explanation": "Sum = -2/k, Product = 3k/k = 3. Given -2/k = 3, so k = -2/3",
                    "difficulty": "Medium"
                }
            ],
            "created_by": "system",
            "created_at": datetime.now(timezone.utc).isoformat()
        }
    ]
    
    for paper in sample_papers:
        existing = await db.papers.find_one({"paper_id": paper["paper_id"]})
        if not existing:
            await db.papers.insert_one(paper)
    
    # Create admin user if not exists
    admin = await db.users.find_one({"email": ADMIN_EMAIL})
    if not admin:
        admin_doc = {
            "user_id": f"admin_{uuid.uuid4().hex[:12]}",
            "email": ADMIN_EMAIL,
            "name": "Admin",
            "role": "admin",
            "password": hash_password(ADMIN_PASSWORD),
            "picture": None,
            "is_approved": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.users.insert_one(admin_doc)
    
    return {"message": "Sample data seeded successfully"}

# Root endpoint
@api_router.get("/")
async def root():
    return {"message": "Education Platform API", "status": "running"}

# Include router
app.include_router(api_router)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
