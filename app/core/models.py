from datetime import datetime
from typing import Optional,List
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime,Text
from sqlalchemy.orm import Mapped, mapped_column,relationship
from app.core.database import Base


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    company: Mapped[str] = mapped_column(String(255), nullable=False)
    location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, default="NA")
    employment_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    apply_link: Mapped[Optional[str]] = mapped_column(String(1000), nullable=False)

    posted_date: Mapped[Optional[datetime]] = mapped_column(DateTime,nullable=True)
    deadline: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    source: Mapped[Optional[str]] = mapped_column(String(255), nullable=False)

    first_seen: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow,nullable=False)
    last_seen: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow,nullable=False)

    applications: Mapped[List["Application"]] = relationship("Application", back_populates="job")

class Application(Base):
    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    job_id: Mapped[int] = mapped_column(Integer, ForeignKey("jobs.id"), nullable=False)

    company: Mapped[str] = mapped_column(String(255), nullable=False)
    role_title: Mapped[str] = mapped_column(String(255), nullable=False)
    apply_url: Mapped[str] = mapped_column(String(1000), nullable=False)

    status: Mapped[str] = mapped_column(String(100), default="Planned", nullable=False)
    applied_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    last_updated: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    priority: Mapped[Optional[int]] = mapped_column(Integer, default=3,nullable=False)

    job : Mapped["Job"] = relationship("Job", back_populates="applications")  
    events: Mapped[List["ApplicationEvent"]] = relationship("ApplicationEvent", back_populates="application")

class ApplicationEvent(Base):
    __tablename__ = "application_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    application_id: Mapped[int] = mapped_column(Integer, ForeignKey("applications.id"), nullable=False)

    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    event_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    application : Mapped["Application"] = relationship("Application", back_populates="events")


class Connection(Base):
    __tablename__ = "connections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    Current_company: Mapped[Optional[str]] = mapped_column(String(255), index=True)
    email_message_id: Mapped[Optional[str]] = mapped_column(String(255), unique=True)
    accepted_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ReferralOpportunity(Base):
    __tablename__ = "referral_opportunities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    job_id: Mapped[int] = mapped_column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), index=True)
    connection_id: Mapped[int] = mapped_column(Integer, ForeignKey("connections.id", ondelete="CASCADE"), index=True)
    
    status: Mapped[str] = mapped_column(String(50), default="new") # e.g., contacted, ignored, done
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)