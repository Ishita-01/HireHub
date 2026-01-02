from app.scraper.base import ScrappedJob
import pandas as pd

INCLUDE_KEYWORDS = [
    "software engineer",
    "software developer",
    "sde",
    "backend engineer",
    "machine learning engineer",
    "ml engineer",
    "ai engineer",
    "applied scientist",
    "summer intern",
    "software development engineer",
    
]

EXCLUDE_KEYWORDS = [
    "senior",
    "staff",
    "principal",
    "manager",
    "lead",
]

INTERNSHIP_KEYWORDS = ["intern", "internship", "6 month", "6-month", "6 months","2-month","2 month","2 months","summer intern","summer internship"]
NEWGRAD_KEYWORDS = ["new grad", "university graduate", "entry level", "grad software"]

PREFERRED_LOCATIONS = ["india", "bangalore", "bengaluru", "hyderabad", "gurgaon","Pune","Mumbai","remote"]

def is_relevant(job: ScrappedJob) -> bool:

    location = job.location
    if pd.isna(location) or location is None:
        loc_text = ""
    else:
        loc_text = str(location).lower()

    text = f"{job.title} {job.employment_type}".lower()

    include = any(k in text for k in INCLUDE_KEYWORDS)
    exclude = any(k in text for k in EXCLUDE_KEYWORDS)
    if not include or exclude:
        return False

    full_text = text
    has_intern = any(k in full_text for k in INTERNSHIP_KEYWORDS)
    has_newgrad = any(k in full_text for k in NEWGRAD_KEYWORDS)

    if not (has_intern or has_newgrad):
        # allow if not explicitly senior but still SWE-ish
        if "3+ years" in full_text or "5+ years" in full_text:
            return False

    loc_text = (job.location or "").lower()
    if PREFERRED_LOCATIONS:
        if not any(loc in loc_text for loc in PREFERRED_LOCATIONS):
            if "remote" not in loc_text:
                return False

    return True

