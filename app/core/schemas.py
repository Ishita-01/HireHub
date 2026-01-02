from datetime import datetime
from pydantic import BaseModel, HttpUrl
from typing import Optional,List


class SchemaBase(BaseModel):
    class Config:
        from_attributes = True


class JobBase(SchemaBase):
    title: str
    company: str
    location: Optional[str] = None
    employment_type: Optional[str] = None
    apply_link: HttpUrl
    deadline: Optional[datetime] = None
    source: Optional[str] = None

class JobCreate(JobBase):
    pass

class JobRead(JobBase):
    id: int
    first_seen: datetime
    last_seen: datetime


class ApplicationBase(BaseModel):
    status: str = "Planned"
    priority: int = 3
    notes: Optional[str] = None

class ApplicationCreate(ApplicationBase):
    job_id: int  # Required to link the application to a job

class ApplicationRead(ApplicationBase, SchemaBase):
    id: int
    company: str
    role_title: str
    apply_url: str
    applied_date: datetime


class userCreate(SchemaBase):
    email: str
    role: str
    resume: str

class UserRead(SchemaBase):
    id: int
    email: str
    role: str
    resume: str

    class config:
        from_attributes = True