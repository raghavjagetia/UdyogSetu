import datetime as dt

from sqlalchemy.orm import Session

from .. import models

SIZE_RANK = {"Micro": 0, "Small": 1, "Medium": 2, "Large": 3}


def rule_applies(rule: models.Rule, sector: str, location: str, size: str) -> bool:
    if not rule.active:
        return False
    if rule.sector != "All" and rule.sector != sector:
        return False
    if rule.location != "All" and rule.location != location:
        return False
    if SIZE_RANK.get(size, 0) < SIZE_RANK.get(rule.min_size, 0):
        return False
    return True


def generate_checklist(db: Session, application: models.Application) -> list[models.ChecklistItem]:
    """Rules-as-code checklist generation: matches active Rule rows against the
    application's sector / location / size and materializes ChecklistItem rows
    with a computed SLA due date. This is the deterministic MVP checklist engine;
    risk-based scrutiny / NLP classification are on the roadmap, not implemented here.
    """
    rules = db.query(models.Rule).filter(models.Rule.active == True).all()  # noqa: E712
    items: list[models.ChecklistItem] = []
    now = dt.datetime.utcnow()

    for rule in rules:
        if rule_applies(rule, application.sector, application.location, application.size):
            item = models.ChecklistItem(
                application_id=application.id,
                rule_id=rule.id,
                approval_name=rule.approval_name,
                department=rule.department,
                clause_ref=rule.clause_ref,
                sla_days=rule.sla_days,
                due_at=now + dt.timedelta(days=rule.sla_days),
                mandatory=rule.mandatory,
                status="pending",
            )
            db.add(item)
            items.append(item)

    db.commit()
    for item in items:
        db.refresh(item)
    return items
