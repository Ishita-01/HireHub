from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from fastapi import FastAPI, Form,Request,Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from .database import Base, engine, SessionLocal
from .deps import get_db
from .models import Job,Application
from app.services.ingest import ingest_jobs
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

@app.get("/scrape-test")
async def trigger_sync(db: Session = Depends(get_db)):
    
    count = ingest_jobs(db) 
    return RedirectResponse(url="/jobs", status_code=303)

@app.get("/jobs", response_class=HTMLResponse)
async def list_jobs(request: Request, db: Session = Depends(get_db)):
    jobs = db.query(Job).order_by(Job.posted_date.desc()).all()
    
    return templates.TemplateResponse(
        "jobs.html", 
        {"request": request, "jobs": jobs}
    )

@app.post("/track-job")
async def track_job(job_id: Annotated[int, Form()], db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        return RedirectResponse(url="/jobs", status_code=303)

    existing_job = db.query(Application).filter(Application.job_id == job_id).first()
    if not existing_job:
        newApplication = Application(
            job_id=job.id,
            company=job.company,
            role_title=job.title,
            apply_url=job.apply_link,
            status="Planned"
        )
            
        
        db.add(newApplication)
        db.commit()
    return RedirectResponse(url="/applications", status_code=303)


@app.get("/applications", response_class=HTMLResponse)
async def view_applications(request: Request, db: Session = Depends(get_db)):
    application = db.query(Application).order_by(Application.applied_date.desc()).all()
    return templates.TemplateResponse(
        "application.html", 
        {"request": request, "applications": application}
    )

@app.post("/update-status")
async def update_app_status(
    app_id: Annotated[int, Form()], 
    new_status: Annotated[str, Form()], 
    db: Session = Depends(get_db)
):
    # Find the application in the database
    application = db.query(Application).filter(Application.id == app_id).first()
    
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