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


class ConnectionCreate(BaseModel):
    name: str
    Current_company: Optional[str] = None
    email_message_id: Optional[str] = None

class ConnectionRead(ConnectionCreate, SchemaBase):
    id: int
    accepted_at: datetime

class ReferralOpportunityRead(SchemaBase):
    id: int
    job_id: int
    connection_id: int
    status: str
    created_at: datetime