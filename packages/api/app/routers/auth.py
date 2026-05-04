"""인증 라우터: 회원가입, 로그인, 토큰 갱신, 사용자 관리"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.config import Settings, get_settings
from app.models.company import Company
from app.models.user import User, UserRole
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    RefreshRequest,
    UserResponse,
    CreateUserRequest,
)
from app.services.auth_service import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.dependencies import get_current_user, require_role

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse)
def register(
    req: RegisterRequest,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    # 이메일 중복 체크
    if db.query(User).filter(User.email == req.email).first():
        raise HTTPException(status_code=400, detail="이미 등록된 이메일입니다")

    # 사업자번호 중복 체크
    if req.business_number:
        if db.query(Company).filter(Company.business_number == req.business_number).first():
            raise HTTPException(status_code=400, detail="이미 등록된 사업자번호입니다")

    # 기업 ��성
    company = Company(name=req.company_name, business_number=req.business_number)
    db.add(company)
    db.flush()

    # 관리자 유저 생성
    user = User(
        company_id=company.id,
        email=req.email,
        password_hash=hash_password(req.password),
        name=req.name,
        role=UserRole.admin.value,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return TokenResponse(
        access_token=create_access_token(user.id, company.id, user.role, settings),
        refresh_token=create_refresh_token(user.id, settings),
    )


@router.post("/login", response_model=TokenResponse)
def login(
    req: LoginRequest,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    user = db.query(User).filter(User.email == req.email).first()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="이메일 또는 비밀번호가 올바르지 않습니다")

    return TokenResponse(
        access_token=create_access_token(user.id, user.company_id, user.role, settings),
        refresh_token=create_refresh_token(user.id, settings),
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh(
    req: RefreshRequest,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    payload = decode_token(req.refresh_token, settings)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="유효하지 않은 리프레시 토큰입니다")

    user = db.query(User).filter(User.id == payload["sub"]).first()
    if not user:
        raise HTTPException(status_code=401, detail="사용자를 찾을 수 없습니다")

    return TokenResponse(
        access_token=create_access_token(user.id, user.company_id, user.role, settings),
        refresh_token=create_refresh_token(user.id, settings),
    )


@router.get("/me", response_model=UserResponse)
def me(user: User = Depends(get_current_user)):
    return user


@router.post("/users", response_model=UserResponse)
def create_user(
    req: CreateUserRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(require_role(UserRole.admin)),
):
    if req.role not in (UserRole.field_manager.value, UserRole.worker.value):
        raise HTTPException(status_code=400, detail="role은 field_manager 또는 worker만 가능합니다")

    if db.query(User).filter(User.email == req.email).first():
        raise HTTPException(status_code=400, detail="이미 등록된 이메일입니다")

    user = User(
        company_id=admin.company_id,
        email=req.email,
        password_hash=hash_password(req.password),
        name=req.name,
        role=req.role,
        site_id=req.site_id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
