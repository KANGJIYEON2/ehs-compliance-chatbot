"""사업장 CRUD 라우터"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User, UserRole
from app.models.site import Site
from app.schemas.site import SiteCreate, SiteUpdate, SiteResponse
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/sites", tags=["sites"])


def _check_site_access(site: Site, user: User) -> None:
    if site.company_id != user.company_id:
        raise HTTPException(status_code=404, detail="사업장을 찾을 수 없습니다")
    if user.role == UserRole.field_manager.value and user.site_id != site.id:
        raise HTTPException(status_code=403, detail="해당 사업장에 대한 권한이 없습니다")


@router.get("", response_model=list[SiteResponse])
def list_sites(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    query = db.query(Site).filter(Site.company_id == user.company_id)
    if user.role == UserRole.field_manager.value and user.site_id:
        query = query.filter(Site.id == user.site_id)
    return query.all()


@router.post("", response_model=SiteResponse, status_code=201)
def create_site(
    req: SiteCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if user.role not in (UserRole.admin.value, UserRole.superadmin.value):
        raise HTTPException(status_code=403, detail="관리자만 사업장을 생성할 수 있습니다")

    site = Site(company_id=user.company_id, name=req.name, address=req.address)
    db.add(site)
    db.commit()
    db.refresh(site)
    return site


@router.get("/{site_id}", response_model=SiteResponse)
def get_site(
    site_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    site = db.query(Site).filter(Site.id == site_id).first()
    if not site:
        raise HTTPException(status_code=404, detail="사업장을 찾을 수 없습니다")
    _check_site_access(site, user)
    return site


@router.patch("/{site_id}", response_model=SiteResponse)
def update_site(
    site_id: str,
    req: SiteUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if user.role not in (UserRole.admin.value, UserRole.superadmin.value):
        raise HTTPException(status_code=403, detail="관리자만 수정할 수 있습니다")

    site = db.query(Site).filter(Site.id == site_id).first()
    if not site:
        raise HTTPException(status_code=404, detail="사업장을 찾을 수 없습니다")
    _check_site_access(site, user)

    if req.name is not None:
        site.name = req.name
    if req.address is not None:
        site.address = req.address
    db.commit()
    db.refresh(site)
    return site


@router.delete("/{site_id}", status_code=204)
def delete_site(
    site_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if user.role not in (UserRole.admin.value, UserRole.superadmin.value):
        raise HTTPException(status_code=403, detail="관리자만 삭제할 수 있습니다")

    site = db.query(Site).filter(Site.id == site_id).first()
    if not site:
        raise HTTPException(status_code=404, detail="사업장을 찾을 수 없습니다")
    _check_site_access(site, user)

    db.delete(site)
    db.commit()
