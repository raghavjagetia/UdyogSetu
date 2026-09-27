import datetime as dt
from typing import Optional, List

from pydantic import BaseModel, EmailStr, Field, ConfigDict


# ---------- Auth / Users ----------

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(min_length=6)
    role: str = Field(pattern="^(entrepreneur|officer|admin)$")
    department: Optional[str] = None


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    role: str
    department: Optional[str] = None
    created_at: dt.datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# ---------- Rules ----------

class RuleCreate(BaseModel):
    sector: str = "All"
    location: str = "All"
    min_size: str = "Micro"
    approval_name: str
    department: str
    clause_ref: str
    sla_days: int = 15
    mandatory: bool = True
    active: bool = True


class RuleUpdate(BaseModel):
    sector: Optional[str] = None
    location: Optional[str] = None
    min_size: Optional[str] = None
    approval_name: Optional[str] = None
    department: Optional[str] = None
    clause_ref: Optional[str] = None
    sla_days: Optional[int] = None
    mandatory: Optional[bool] = None
    active: Optional[bool] = None


class RuleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    sector: str
    location: str
    min_size: str
    approval_name: str
    department: str
    clause_ref: str
    sla_days: int
    mandatory: bool
    active: bool


# ---------- Documents ----------

class DocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    original_filename: str
    uploaded_at: dt.datetime


# ---------- Checklist ----------

class ChecklistItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    application_id: int
    approval_name: str
    department: str
    clause_ref: str
    sla_days: int
    due_at: dt.datetime
    mandatory: bool
    status: str
    remarks: Optional[str] = None
    reviewed_by: Optional[int] = None
    reviewed_at: Optional[dt.datetime] = None
    documents: List[DocumentOut] = []


class ChecklistReviewRequest(BaseModel):
    action: str = Field(pattern="^(approve|reject)$")
    remarks: Optional[str] = None


# ---------- Applications ----------

class ApplicationCreate(BaseModel):
    project_name: str
    sector: str
    location: str
    size: str = Field(pattern="^(Micro|Small|Medium|Large)$")
    stage: str = Field(pattern="^(New|Expansion|Existing)$")


class ApplicationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    applicant_id: int
    project_name: str
    sector: str
    location: str
    size: str
    stage: str
    status: str
    created_at: dt.datetime
    updated_at: dt.datetime


class ApplicationDetailOut(ApplicationOut):
    checklist_items: List[ChecklistItemOut] = []
    applicant_name: Optional[str] = None
    applicant_email: Optional[str] = None


# ---------- Schemes ----------

class SchemeCreate(BaseModel):
    name: str
    sector: str = "All"
    description: str
    benefits: str
    active: bool = True


class SchemeUpdate(BaseModel):
    name: Optional[str] = None
    sector: Optional[str] = None
    description: Optional[str] = None
    benefits: Optional[str] = None
    active: Optional[bool] = None


class SchemeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    sector: str
    description: str
    benefits: str
    active: bool


# ---------- Dashboard ----------

class StatusCount(BaseModel):
    status: str
    count: int


class SectorCount(BaseModel):
    sector: str
    count: int


class DepartmentPending(BaseModel):
    department: str
    pending: int
    overdue: int


class DashboardStats(BaseModel):
    total_applications: int
    approved: int
    rejected: int
    in_progress: int
    overdue_items: int
    avg_turnaround_days: Optional[float] = None
    by_status: List[StatusCount]
    by_sector: List[SectorCount]
    by_department: List[DepartmentPending]
