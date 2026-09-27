from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..auth import require_roles
from ..database import get_db
from ..seed_data import LOCATIONS, SECTORS

router = APIRouter(prefix="/api/rules", tags=["rules"])


@router.get("/meta")
def get_meta():
    return {"sectors": SECTORS, "locations": LOCATIONS, "sizes": ["Micro", "Small", "Medium", "Large"]}


@router.get("", response_model=list[schemas.RuleOut])
def list_rules(db: Session = Depends(get_db), _: models.User = Depends(require_roles("admin", "officer", "entrepreneur"))):
    return db.query(models.Rule).order_by(models.Rule.sector, models.Rule.approval_name).all()


@router.post("", response_model=schemas.RuleOut, status_code=201)
def create_rule(
    payload: schemas.RuleCreate, db: Session = Depends(get_db), _: models.User = Depends(require_roles("admin"))
):
    rule = models.Rule(**payload.model_dump())
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule


@router.put("/{rule_id}", response_model=schemas.RuleOut)
def update_rule(
    rule_id: int,
    payload: schemas.RuleUpdate,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_roles("admin")),
):
    rule = db.query(models.Rule).filter(models.Rule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(rule, key, value)
    db.commit()
    db.refresh(rule)
    return rule


@router.delete("/{rule_id}", status_code=204)
def delete_rule(rule_id: int, db: Session = Depends(get_db), _: models.User = Depends(require_roles("admin"))):
    rule = db.query(models.Rule).filter(models.Rule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    db.delete(rule)
    db.commit()
    return None
