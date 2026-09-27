import datetime as dt
import os
import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from .. import models, schemas
from ..auth import get_current_user, require_roles
from ..config import UPLOAD_DIR
from ..database import get_db
from ..rules_engine.engine import generate_checklist

router = APIRouter(prefix="/api/applications", tags=["applications"])

ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".doc", ".docx"}


def _recompute_status(application: models.Application) -> None:
    items = application.checklist_items
    if not items:
        return
    mandatory_items = [i for i in items if i.mandatory] or items
    mandatory_statuses = [i.status for i in mandatory_items]
    all_statuses = [i.status for i in items]

    if any(s == "rejected" for s in mandatory_statuses):
        application.status = "rejected"
    elif all(s == "approved" for s in mandatory_statuses):
        application.status = "approved"
    elif any(s != "pending" for s in all_statuses):
        application.status = "under_review"
    else:
        application.status = "submitted"


def _to_detail(application: models.Application) -> schemas.ApplicationDetailOut:
    data = schemas.ApplicationDetailOut.model_validate(application)
    data.applicant_name = application.applicant.name
    data.applicant_email = application.applicant.email
    return data


@router.post("", response_model=schemas.ApplicationDetailOut, status_code=201)
def create_application(
    payload: schemas.ApplicationCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(require_roles("entrepreneur")),
):
    application = models.Application(
        applicant_id=user.id,
        project_name=payload.project_name,
        sector=payload.sector,
        location=payload.location,
        size=payload.size,
        stage=payload.stage,
        status="submitted",
    )
    db.add(application)
    db.commit()
    db.refresh(application)

    generate_checklist(db, application)
    db.refresh(application)
    return _to_detail(application)


@router.get("", response_model=list[schemas.ApplicationDetailOut])
def list_applications(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    query = db.query(models.Application)

    if user.role == "entrepreneur":
        query = query.filter(models.Application.applicant_id == user.id)
    elif user.role == "officer":
        query = (
            query.join(models.ChecklistItem)
            .filter(models.ChecklistItem.department == user.department)
            .distinct()
        )
    # admin sees everything

    applications = query.order_by(models.Application.created_at.desc()).all()
    return [_to_detail(a) for a in applications]


def _get_application_or_404(db: Session, application_id: int) -> models.Application:
    application = db.query(models.Application).filter(models.Application.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    return application


def _authorize_view(application: models.Application, user: models.User) -> None:
    if user.role == "admin":
        return
    if user.role == "entrepreneur" and application.applicant_id == user.id:
        return
    if user.role == "officer" and any(i.department == user.department for i in application.checklist_items):
        return
    raise HTTPException(status_code=403, detail="You do not have access to this application")


@router.get("/{application_id}", response_model=schemas.ApplicationDetailOut)
def get_application(
    application_id: int, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)
):
    application = _get_application_or_404(db, application_id)
    _authorize_view(application, user)
    return _to_detail(application)


@router.post("/{application_id}/checklist/{item_id}/document", response_model=schemas.ChecklistItemOut)
def upload_document(
    application_id: int,
    item_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: models.User = Depends(require_roles("entrepreneur")),
):
    application = _get_application_or_404(db, application_id)
    if application.applicant_id != user.id:
        raise HTTPException(status_code=403, detail="You do not have access to this application")

    item = next((i for i in application.checklist_items if i.id == item_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="Checklist item not found")

    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext or 'unknown'}")

    stored_name = f"{uuid.uuid4().hex}{ext}"
    dest_path = os.path.join(UPLOAD_DIR, stored_name)
    with open(dest_path, "wb") as out:
        out.write(file.file.read())

    document = models.Document(
        checklist_item_id=item.id,
        original_filename=file.filename or stored_name,
        stored_filename=stored_name,
    )
    db.add(document)

    item.status = "document_uploaded"
    _recompute_status(application)
    db.commit()
    db.refresh(item)
    return item


@router.post("/{application_id}/checklist/{item_id}/review", response_model=schemas.ChecklistItemOut)
def review_checklist_item(
    application_id: int,
    item_id: int,
    payload: schemas.ChecklistReviewRequest,
    db: Session = Depends(get_db),
    user: models.User = Depends(require_roles("officer", "admin")),
):
    application = _get_application_or_404(db, application_id)
    item = next((i for i in application.checklist_items if i.id == item_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="Checklist item not found")

    if user.role == "officer" and item.department != user.department:
        raise HTTPException(status_code=403, detail="This item belongs to a different department")

    item.status = "approved" if payload.action == "approve" else "rejected"
    item.remarks = payload.remarks
    item.reviewed_by = user.id
    item.reviewed_at = dt.datetime.utcnow()

    log = models.ApprovalLog(
        checklist_item_id=item.id, actor_id=user.id, action=payload.action, remarks=payload.remarks
    )
    db.add(log)

    _recompute_status(application)
    db.commit()
    db.refresh(item)
    return item
