import csv
import datetime as dt
import io

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from .. import models, schemas
from ..auth import get_current_user, require_roles
from ..database import get_db

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


def _visible_applications(db: Session, user: models.User):
    query = db.query(models.Application)
    if user.role == "entrepreneur":
        query = query.filter(models.Application.applicant_id == user.id)
    elif user.role == "officer":
        query = (
            query.join(models.ChecklistItem)
            .filter(models.ChecklistItem.department == user.department)
            .distinct()
        )
    return query.all()


@router.get("/stats", response_model=schemas.DashboardStats)
def get_stats(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    applications = _visible_applications(db, user)
    now = dt.datetime.utcnow()

    status_counts: dict[str, int] = {}
    sector_counts: dict[str, int] = {}
    dept_pending: dict[str, dict[str, int]] = {}
    overdue_items = 0
    turnaround_days: list[float] = []

    for app in applications:
        status_counts[app.status] = status_counts.get(app.status, 0) + 1
        sector_counts[app.sector] = sector_counts.get(app.sector, 0) + 1

        if app.status in ("approved", "rejected"):
            delta = (app.updated_at - app.created_at).total_seconds() / 86400
            turnaround_days.append(max(delta, 0))

        for item in app.checklist_items:
            if user.role == "officer" and item.department != user.department:
                continue
            bucket = dept_pending.setdefault(item.department, {"pending": 0, "overdue": 0})
            if item.status not in ("approved", "rejected"):
                bucket["pending"] += 1
                if item.due_at < now:
                    bucket["overdue"] += 1
                    overdue_items += 1

    return schemas.DashboardStats(
        total_applications=len(applications),
        approved=status_counts.get("approved", 0),
        rejected=status_counts.get("rejected", 0),
        in_progress=len(applications) - status_counts.get("approved", 0) - status_counts.get("rejected", 0),
        overdue_items=overdue_items,
        avg_turnaround_days=round(sum(turnaround_days) / len(turnaround_days), 1) if turnaround_days else None,
        by_status=[schemas.StatusCount(status=k, count=v) for k, v in status_counts.items()],
        by_sector=[schemas.SectorCount(sector=k, count=v) for k, v in sector_counts.items()],
        by_department=[
            schemas.DepartmentPending(department=k, pending=v["pending"], overdue=v["overdue"])
            for k, v in dept_pending.items()
        ],
    )


@router.get("/export")
def export_report(db: Session = Depends(get_db), _: models.User = Depends(require_roles("admin"))):
    applications = db.query(models.Application).order_by(models.Application.created_at.desc()).all()

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(
        [
            "Application ID", "Project Name", "Applicant", "Sector", "Location", "Size", "Stage",
            "Status", "Created At", "Checklist Item", "Department", "Item Status", "SLA Due",
        ]
    )
    for app in applications:
        if not app.checklist_items:
            writer.writerow(
                [app.id, app.project_name, app.applicant.email, app.sector, app.location, app.size,
                 app.stage, app.status, app.created_at.isoformat(), "", "", "", ""]
            )
        for item in app.checklist_items:
            writer.writerow(
                [
                    app.id, app.project_name, app.applicant.email, app.sector, app.location, app.size,
                    app.stage, app.status, app.created_at.isoformat(),
                    item.approval_name, item.department, item.status, item.due_at.isoformat(),
                ]
            )

    buffer.seek(0)
    return StreamingResponse(
        buffer,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=udyogsetu_compliance_report.csv"},
    )
