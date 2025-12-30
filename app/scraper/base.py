from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional

class ScrappedJob():
    def __init__(
        self,
        job_title: str,
        company: str,
        employment_type: str,
        location: str,
        apply_link: str,
        posted_date: Optional[datetime] = None,
        deadline: Optional[datetime] = None,
    ):
        self.job_title = job_title
        self.company = company
        self.employment_type = employment_type
        self.location = location
        self.apply_link = apply_link
        self.posted_date = posted_date
        self.deadline = deadline

class BaseScraper(ABC):
    @abstractmethod
    def scrape_jobs(self) -> List[ScrappedJob]:
        """Scrape job listings from a source.

        Returns:
            List[ScrappedJob]: A list of scrapped job listings.
        """
        pass
        