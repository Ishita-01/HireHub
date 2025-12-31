from contextlib import asynccontextmanager
from fastapi import FastAPI,Request,Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from .database import Base, engine
from .deps import get_db
from .models import Job


@asynccontextmanager
async def lifespan(app: FastAPI):
    
    Base.metadata.create_all(bind=engine)
    yield  
    pass

app = FastAPI(lifespan=lifespan)

@app.get("/jobs", response_class=HTMLResponse)
async def list_jobs(request: Request, db: Session = Depends(get_db)):
    jobs = db.query(Job).order_by(Job.posted_date.desc()).all()
    templates = Jinja2Templates(directory="app/templates")
    return templates.TemplateResponse(
        "jobs.html", 
        {"request": request, "jobs": jobs}
    )