from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from http.client import HTTPException
import os
from fastapi import FastAPI, Form,Request,Depends, File, UploadFile
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from sqlalchemy.orm import Session
from .database import Base, engine, SessionLocal
from .deps import auth_required, get_db,get_current_user,roleRequired
from .schemas import userCreate
from .models import Job,Application,User,UserRole
from app.services.ingest import ingest_jobs
from app.services.analyzer import analyze_resume
from typing import Annotated



@asynccontextmanager
async def lifespan(app: FastAPI):
    
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        now = datetime.utcnow()
        db.query(Job).filter(Job.deadline < now).delete()
        expiry_limit = now - timedelta(days=15)
        
        db.query(Job).filter(
            Job.deadline == None,           # Only jobs with no deadline
            Job.first_seen < expiry_limit   # Older than 15 days
        ).delete()
        
        db.commit()
    except Exception as e:
        print(f"Cleanup error: {e}")
    finally:
        db.close()
        
    yield
    pass

app = FastAPI(lifespan=lifespan)
templates = Jinja2Templates(directory="app/templates")

def createUser(db: Session,userData:userCreate):
    if userData.username == "ishita@admin" :
        role = "admin"
    else:
        role = "user"
    
    newUser = User(
        username=userData.username,
        email=userData.email,
        password=userData.password,
        role=role,
        resume = userData.resume
    )
    db.add(newUser)
    db.commit()
    return newUser


@app.get("/analyze", response_class=HTMLResponse)
async def analyze_page(request: Request, user: User = Depends(auth_required)):
    """Render the standalone analysis page."""
    return templates.TemplateResponse("analyze.html", {"request": request, "user": user})

@app.post("/analyze-resume")
async def analyze_resume_req(
    request: Request,
    job_description: Annotated[str, Form()],
    user: User = Depends(auth_required)
):
    """Handle the AI analysis and stay on the analysis page."""
    if not user.resume or not os.path.exists(user.resume):
        return RedirectResponse(url="/profile?error=no_resume", status_code=303)

    # Call Gemini service with the full PDF path
    analysis = analyze_resume(user.resume, job_description)

    return templates.TemplateResponse("analyze.html", {
        "request": request,
        "user": user,
        "analysis": analysis,
        "jd": job_description
    })



# app/core/main.py

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve the landing page."""
    return templates.TemplateResponse("home.html", {"request": request,"user": None})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Serve the login page."""
    return templates.TemplateResponse("login.html", {"request": request,"user": None})
@app.post("/login")
async def handle_login(
    request: Request,
    username: Annotated[str, Form()],
    #email: Annotated[str, Form()],
    password: Annotated[str, Form()],
    #resume: Annotated[str, Form()] = None,
    db: Session = Depends(get_db)
):
    
    user = db.query(User).filter(User.username == username).first()
    if not user or user.hashed_password != password:
        return (templates.TemplateResponse(
            "login.html",
              {"request": request,
               "user": None,
               "error":"Invalid credentials"
            }))
    
    response = RedirectResponse(url="/jobs", status_code=303)
    response.set_cookie(key="session_user", value=user.username)
    
    return response

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):

    """Route for new user registration."""
    return templates.TemplateResponse("register.html", {"request": request,"user": None})
@app.post("/register")
async def handle_registration(
    username: Annotated[str, Form()],
    email: Annotated[str, Form()],
    password: Annotated[str, Form()],
    resume: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    if not resume or not resume.filename:
        return RedirectResponse(url="/register?error=no_file", status_code=303)
    resume_path = None
    if resume and resume.filename:
        os.makedirs("uploads/resumes", exist_ok=True)
        resume_path = f"uploads/resumes/{username}_{resume.filename}"
        with open(resume_path, "wb") as f:
            f.write(await resume.read())
    
    # Determine role based on username
    role = UserRole.ADMIN if username == "ishita@admin" else UserRole.USER
    
    # In a real app, you would hash the password here (e.g., using passlib)
    hashed_pwd = password # Replace with pwd_context.hash(password)
    
    new_user = User(
        username=username,
        email=email,
        hashed_password=hashed_pwd,
        role=role,
        resume=resume_path
    )
    
    try:
        db.add(new_user)
        db.commit()
    except Exception as e:
        db.rollback()
        # You should handle duplicate username/email errors here
        print(f"Registration Error: {e}")
        return RedirectResponse(url="/register?error=exists", status_code=303)
        
    return RedirectResponse(url="/login?success=registered", status_code=303)


@app.get("/logout")
async def logout(request: Request):
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie(key="session_user")
    return response

@app.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request, user: User = Depends(auth_required)):
    return templates.TemplateResponse("profile.html", {"request": request, "user": user})


@app.post("/update-resume")
async def update_resume(
    resume: UploadFile = File(None),
    db: Session = Depends(get_db),
    user: User = Depends(auth_required)
):
    if not resume or not resume.filename:
        return RedirectResponse(url="/profile?error=no_file", status_code=303)
    
    resume_path = None
    if resume and resume.filename:
        os.makedirs("uploads/resumes", exist_ok=True)
        resume_path = f"uploads/resumes/{user.username}_{resume.filename}"
        with open(resume_path, "wb") as f:
            f.write(await resume.read())
    
    user.resume = resume_path
    db.commit()
    
    return RedirectResponse(url="/profile?success=updated", status_code=303)


@app.get("/view-resume")
async def view_resume(user: User = Depends(auth_required)):
    """Serves the user's current resume PDF."""
    if not user.resume or not os.path.exists(user.resume):
        raise HTTPException(status_code=404, detail="Resume file not found.")
    
    return FileResponse(
        path=user.resume, 
        media_type='application/pdf',
        filename=os.path.basename(user.resume)
    )

@app.get("/scrape-test")
async def trigger_sync(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.username != "ishita@admin" or current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized to perform this action.")
    
    count = ingest_jobs(db) 
    return RedirectResponse(url="/jobs", status_code=303)

@app.get("/jobs", response_class=HTMLResponse)
async def list_jobs(
    request: Request, 
    db: Session = Depends(get_db),
    source: str = None,
    current_user: User = Depends(auth_required)
    ):
    jobs = db.query(Job).order_by(Job.posted_date.desc()).all()
    query = db.query(Job)
    if source == "onCampus":
        query = query.filter(Job.source == "onCampus")
    elif source == "web":
        query = query.filter(Job.source != "onCampus")
    
    jobs = query.all()

    
    return templates.TemplateResponse("jobs.html", {
        "request": request,
        "jobs": jobs,
        "user":current_user,
        "current_source":source
    })

@app.post("/track-job")
async def track_job(
    job_id: Annotated[int, Form()],
    current_user: User = Depends(auth_required),
    db: Session = Depends(get_db)
    ):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        return RedirectResponse(url="/jobs", status_code=303)

    existing_job = db.query(Application).filter(Application.job_id == job_id, Application.user_id == current_user.id).first()
    if not existing_job:
        newApplication = Application(
            job_id=job.id,
            user_id=current_user.id,
            company=job.company,
            role_title=job.title,
            apply_url=job.apply_link,
            status="Planned"
        )
            
        
        db.add(newApplication)
        db.commit()
    return RedirectResponse(url="/applications", status_code=303)


@app.get("/applications", response_class=HTMLResponse)
async def view_applications(
    request: Request, 
    db: Session = Depends(get_db),
    user = Depends(auth_required)
):
    application = db.query(Application).filter(Application.user_id == user.id).order_by(Application.applied_date.desc()).all()
    return templates.TemplateResponse(
        "application.html", 
        {"request": request, "applications": application,"user":user}
    )

@app.post("/update-status")
async def update_app_status(
    app_id: Annotated[int, Form()], 
    new_status: Annotated[str, Form()], 
    db: Session = Depends(get_db),
    user: User = Depends(auth_required)
):
    # Find the application in the database
    application = db.query(Application).filter(Application.id == app_id, Application.user_id == user.id).first()
    
    if application:
        application.status = new_status
        db.commit() # Save the change
        
    return RedirectResponse(url="/applications", status_code=303)

@app.post("/delete-application")
async def delete_application(
    app_id: Annotated[int, Form()], 
    db: Session = Depends(get_db)
):
    application = db.query(Application).filter(Application.id == app_id).first()
    
    if application:
        db.delete(application)
        db.commit()
        
    return RedirectResponse(url="/applications", status_code=303)

@app.post("/update-notes")
async def update_notes(
        app_id: Annotated[int, Form()],
        notes: Annotated[str, Form()],  
        db: Session = Depends(get_db)
):
    application = db.query(Application).filter(Application.id == app_id).first()
    
    if application:
        application.notes = notes
        db.commit() 
        
    return RedirectResponse(url="/applications", status_code=303)


@app.post("/add-jobs-manually")
async def add_job_manually(
    company: Annotated[str, Form()],
    title: Annotated[str, Form()],
    apply_link: Annotated[str, Form()],
    location: Annotated[str, Form()] ,
    employment_type: Annotated[str, Form()],
    deadline: datetime = Form(None),
    db: Session = Depends(get_db)
):
    new_job = Job(
        company=company,
        title=title,
        apply_link=apply_link,
        location=location,
        employment_type=employment_type,
        deadline=deadline,
        source="Manual Entry",
        posted_date=datetime.utcnow()
    )
    
    db.add(new_job)
    db.commit()
    
    return RedirectResponse(url="/jobs", status_code=303)


@app.post("/edit-job")
async def edit_job(
    job_id: Annotated[int, Form()],
    company: Annotated[str, Form()],
    title: Annotated[str, Form()],
    location: Annotated[str, Form()],
    employment_type: Annotated[str, Form()],
    deadline: Annotated[str, Form()] = None,
    apply_link: Annotated[str, Form()] = None,
    db: Session = Depends(get_db)
):
    job = db.query(Job).filter(Job.id == job_id).first()
    if job:
        job.company = company
        job.title = title
        job.location = location
        job.employment_type = employment_type
        job.apply_link = apply_link
        

        if deadline:
            try:
                job.deadline = datetime.strptime(deadline, "%Y-%m-%d")
            except ValueError:
                pass
                
        db.commit()
    return RedirectResponse(url="/jobs", status_code=303)