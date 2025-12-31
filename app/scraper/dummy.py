from datetime import datetime, timedelta
from .base import BaseScraper, ScrappedJob

class DummyScraper(BaseScraper):
    """Fake scraper just to test the pipeline."""

    def fetch_jobs(self):
        now = datetime.utcnow()
        return [
            ScrappedJob(
                title="Summer Intern (Evergreen)",
                company="Visa",
                location="Bangalore, India",
                employment_type="Internship",
                apply_link="https://smrtr.io/sT_xq",
                posted_date=now - timedelta(days=1),
                
                source="Visa",
            ),
            ScrappedJob(
                title="Software Engineering Intern",
                company="Microsoft",
                location="Bangalore, India",
                employment_type="Internship",
                apply_link="https://apply.careers.microsoft.com/careers/job/1970393556625300?src=KrishanKumarLinkedin",
                posted_date=now - timedelta(days=1),
                source="LinkedIn",
            ),
        ]
