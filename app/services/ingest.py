from sqlalchemy.orm import Session
from app.core.filters import is_relevant
from app.core.models import Job
from app.scraper.dummy import DummyScraper


def ingest_dummy_jobs(db: Session):
    scrapper = DummyScraper()
    foundJobs = scrapper.fetch_jobs()

    newCount = 0
    for job in foundJobs:

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
                posted_date = job.posted_date,
                source = job.source,
            )
            db.add(dbJobs)
            newCount += 1

    db.commit()
    return newCount

