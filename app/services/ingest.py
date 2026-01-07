from sqlalchemy.orm import Session
from app.core.filters import is_relevant
from app.core.gmail_auth import get_gmail_service
from app.core.models import Job
# from app.scraper.dummy import DummyScraper
from app.scraper.liveScrapper import JobSpyScraper
import pandas as pd
from app.scraper.onCampus_Scrapper import OnCampusScraper


def ingest_jobs(db: Session):
    web_scrapper = JobSpyScraper()
    foundJobs = web_scrapper.fetch_jobs()

    campus_scrapper = OnCampusScraper(service= get_gmail_service())
    campus_jobs = campus_scrapper.fetch_jobs()

    newCount = 0
    for job in (campus_jobs + foundJobs):

        posted_date = job.posted_date
        if pd.isna(posted_date):
            posted_date = None

        job.location = None if pd.isna(job.location) else str(job.location)
        job.title = "" if pd.isna(job.title) else str(job.title)
        job.employment_type = "Not Specified" if pd.isna(job.employment_type) else str(job.employment_type)

        if not is_relevant(job):
            continue

        
        
        exists = db.query(Job).filter(Job.apply_link == job.apply_link).first()
        
        if not exists:
            dbJobs = Job(
                title = job.title,
                company = job.company,
                location = job.location,    
                employment_type = job.employment_type,
                apply_link = job.apply_link,
                posted_date = posted_date,
                source = job.source,
            )
            db.add(dbJobs)
            
            newCount += 1

    db.commit()
    return newCount

