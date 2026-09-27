import datetime as dt

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from .database import Base


def utcnow():
    return dt.datetime.utcnow()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    email = Column(String(160), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="entrepreneur")  # entrepreneur | officer | admin
    department = Column(String(120), nullable=True)  # only meaningful for officers
    created_at = Column(DateTime, default=utcnow)

    applications = relationship("Application", back_populates="applicant", foreign_keys="Application.applicant_id")


class Rule(Base):
    """A single regulatory requirement mapped by sector/location, used by the checklist engine."""

    __tablename__ = "rules"

    id = Column(Integer, primary_key=True, index=True)
    sector = Column(String(80), nullable=False, default="All")
    location = Column(String(80), nullable=False, default="All")
    min_size = Column(String(20), nullable=False, default="Micro")  # smallest size this rule applies from
    approval_name = Column(String(160), nullable=False)
    department = Column(String(120), nullable=False)
    clause_ref = Column(String(160), nullable=False)
    sla_days = Column(Integer, nullable=False, default=15)
    mandatory = Column(Boolean, default=True)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utcnow)


class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    applicant_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    project_name = Column(String(160), nullable=False)
    sector = Column(String(80), nullable=False)
    location = Column(String(80), nullable=False)
    size = Column(String(20), nullable=False)  # Micro | Small | Medium | Large
    stage = Column(String(20), nullable=False)  # New | Expansion | Existing
    status = Column(String(20), nullable=False, default="submitted")  # submitted|under_review|approved|rejected
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    applicant = relationship("User", back_populates="applications", foreign_keys=[applicant_id])
    checklist_items = relationship(
        "ChecklistItem", back_populates="application", cascade="all, delete-orphan"
    )


class ChecklistItem(Base):
    __tablename__ = "checklist_items"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id"), nullable=False)
    rule_id = Column(Integer, ForeignKey("rules.id"), nullable=True)
    approval_name = Column(String(160), nullable=False)
    department = Column(String(120), nullable=False)
    clause_ref = Column(String(160), nullable=False)
    sla_days = Column(Integer, nullable=False, default=15)
    due_at = Column(DateTime, nullable=False)
    mandatory = Column(Boolean, default=True)
    status = Column(String(24), nullable=False, default="pending")
    # pending | document_uploaded | under_review | approved | rejected
    remarks = Column(Text, nullable=True)
    reviewed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=utcnow)

    application = relationship("Application", back_populates="checklist_items")
    documents = relationship("Document", back_populates="checklist_item", cascade="all, delete-orphan")


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    checklist_item_id = Column(Integer, ForeignKey("checklist_items.id"), nullable=False)
    original_filename = Column(String(255), nullable=False)
    stored_filename = Column(String(255), nullable=False)
    uploaded_at = Column(DateTime, default=utcnow)

    checklist_item = relationship("ChecklistItem", back_populates="documents")


class Scheme(Base):
    __tablename__ = "schemes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(160), nullable=False)
    sector = Column(String(80), nullable=False, default="All")
    description = Column(Text, nullable=False)
    benefits = Column(Text, nullable=False)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utcnow)


class ApprovalLog(Base):
    __tablename__ = "approval_logs"

    id = Column(Integer, primary_key=True, index=True)
    checklist_item_id = Column(Integer, ForeignKey("checklist_items.id"), nullable=False)
    actor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action = Column(String(40), nullable=False)
    remarks = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utcnow)
