from jobspy import scrape_jobs
from .base import BaseScraper, ScrappedJob
import pandas as pd

class JobSpyScraper(BaseScraper):
    def fetch_jobs(self) -> list[ScrappedJob]:
        jobs = scrape_jobs(
            site_name=["indeed","linkedin","glassdoor","naukri"],
            search_term="software",
            location="india",
            country_at_box='india',
            results_wanted=30,
            hours_old=72,
            country_indeed = "India",
            verbose=2          # Logs will now show you if Indeed returns a 403 or 429 error
        )
        
        scrapped_list = []

        for _, row in jobs.iterrows():
            scrapped_list.append(ScrappedJob(
                title=row['title'],
                company=row['company'],
                location=row['location'] or "Not Specified",
                employment_type=row['job_type'] or "Not Specified",
                posted_date=row['date_posted'],
                apply_link=row['job_url'],
                source=row['site']
            ))
        return scrapped_list
            