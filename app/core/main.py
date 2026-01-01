from contextlib import asynccontextmanager
from fastapi import FastAPI, Form,Request,Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from .database import Base, engine
from .deps import get_db
from .models import Job,Application
from app.services.ingest import ingest_dummy_jobs
from typing import Annotated


@asynccontextmanager
async def lifespan(app: FastAPI):
    
    Base.metadata.create_all(bind=engine)
    yield  
    pass

app = FastAPI(lifespan=lifespan)
templates = Jinja2Templates(directory="app/templates")

@app.get("/scrape-test")
async def trigger_sync(db: Session = Depends(get_db)):
    
    count = ingest_dummy_jobs(db) 
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
        {"request": request, "application": application}
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

