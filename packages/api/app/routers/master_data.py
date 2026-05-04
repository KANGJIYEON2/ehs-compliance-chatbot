"""마스터 데이터 CRUD: 부서, 공정, 장비, 작업구역"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User, UserRole
from app.models.site import Site
from app.models.master_data import Department, Process, Equipment, WorkZone
from app.schemas.master_data import (
    DepartmentCreate,
    DepartmentResponse,
    ProcessCreate,
    ProcessResponse,
    EquipmentCreate,
    EquipmentResponse,
    WorkZoneCreate,
    WorkZoneResponse,
)
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/sites/{site_id}", tags=["master-data"])


def _get_site_checked(site_id: str, user: User, db: Session) -> Site:
    site = db.query(Site).filter(Site.id == site_id).first()
    if not site or site.company_id != user.company_id:
        raise HTTPException(status_code=404, detail="사업장을 찾을 수 없습니다")
    if user.role == UserRole.field_manager.value and user.site_id != site.id:
        raise HTTPException(status_code=403, detail="권한이 없습니다")
    return site


# ── Departments ──

@router.get("/departments", response_model=list[DepartmentResponse])
def list_departments(site_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    _get_site_checked(site_id, user, db)
    return db.query(Department).filter(Department.site_id == site_id).all()


@router.post("/departments", response_model=DepartmentResponse, status_code=201)
def create_department(site_id: str, req: DepartmentCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    _get_site_checked(site_id, user, db)
    obj = Department(site_id=site_id, name=req.name)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/departments/{dept_id}", status_code=204)
def delete_department(site_id: str, dept_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    _get_site_checked(site_id, user, db)
    obj = db.query(Department).filter(Department.id == dept_id, Department.site_id == site_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="부서를 찾을 수 없습니다")
    db.delete(obj)
    db.commit()


# ── Processes ──

@router.get("/processes", response_model=list[ProcessResponse])
def list_processes(site_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    _get_site_checked(site_id, user, db)
    return db.query(Process).filter(Process.site_id == site_id).all()


@router.post("/processes", response_model=ProcessResponse, status_code=201)
def create_process(site_id: str, req: ProcessCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    _get_site_checked(site_id, user, db)
    obj = Process(site_id=site_id, name=req.name)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/processes/{proc_id}", status_code=204)
def delete_process(site_id: str, proc_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    _get_site_checked(site_id, user, db)
    obj = db.query(Process).filter(Process.id == proc_id, Process.site_id == site_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="공정을 찾을 수 없습니다")
    db.delete(obj)
    db.commit()


# ── Equipment ──

@router.get("/equipment", response_model=list[EquipmentResponse])
def list_equipment(site_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    _get_site_checked(site_id, user, db)
    return db.query(Equipment).filter(Equipment.site_id == site_id).all()


@router.post("/equipment", response_model=EquipmentResponse, status_code=201)
def create_equipment(site_id: str, req: EquipmentCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    _get_site_checked(site_id, user, db)
    obj = Equipment(site_id=site_id, name=req.name, process_id=req.process_id)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/equipment/{equip_id}", status_code=204)
def delete_equipment(site_id: str, equip_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    _get_site_checked(site_id, user, db)
    obj = db.query(Equipment).filter(Equipment.id == equip_id, Equipment.site_id == site_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="장비를 찾을 수 없습니다")
    db.delete(obj)
    db.commit()


# ── Work Zones ──

@router.get("/work-zones", response_model=list[WorkZoneResponse])
def list_work_zones(site_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    _get_site_checked(site_id, user, db)
    return db.query(WorkZone).filter(WorkZone.site_id == site_id).all()


@router.post("/work-zones", response_model=WorkZoneResponse, status_code=201)
def create_work_zone(site_id: str, req: WorkZoneCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    _get_site_checked(site_id, user, db)
    obj = WorkZone(site_id=site_id, name=req.name)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/work-zones/{zone_id}", status_code=204)
def delete_work_zone(site_id: str, zone_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    _get_site_checked(site_id, user, db)
    obj = db.query(WorkZone).filter(WorkZone.id == zone_id, WorkZone.site_id == site_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="작업구역을 찾을 수 없습니다")
    db.delete(obj)
    db.commit()
