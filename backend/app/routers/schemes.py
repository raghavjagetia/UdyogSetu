from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..auth import get_current_user, require_roles
from ..database import get_db

router = APIRouter(prefix="/api/schemes", tags=["schemes"])


@router.get("", response_model=list[schemas.SchemeOut])
def list_schemes(db: Session = Depends(get_db), _: models.User = Depends(get_current_user)):
    return db.query(models.Scheme).order_by(models.Scheme.name).all()


@router.post("", response_model=schemas.SchemeOut, status_code=201)
def create_scheme(
    payload: schemas.SchemeCreate, db: Session = Depends(get_db), _: models.User = Depends(require_roles("admin"))
):
    scheme = models.Scheme(**payload.model_dump())
    db.add(scheme)
    db.commit()
    db.refresh(scheme)
    return scheme


@router.put("/{scheme_id}", response_model=schemas.SchemeOut)
def update_scheme(
    scheme_id: int,
    payload: schemas.SchemeUpdate,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_roles("admin")),
):
    scheme = db.query(models.Scheme).filter(models.Scheme.id == scheme_id).first()
    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(scheme, key, value)
    db.commit()
    db.refresh(scheme)
    return scheme


@router.delete("/{scheme_id}", status_code=204)
def delete_scheme(scheme_id: int, db: Session = Depends(get_db), _: models.User = Depends(require_roles("admin"))):
    scheme = db.query(models.Scheme).filter(models.Scheme.id == scheme_id).first()
    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")
    db.delete(scheme)
    db.commit()
    return None
