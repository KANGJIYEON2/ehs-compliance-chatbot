"""SuperAdmin 계정 생성 스크립트"""
import sys
sys.path.insert(0, ".")

from app.config import get_settings
from app.database import init_db, get_db, Base, engine
from app.models import *  # noqa
from app.models.user import User, UserRole
from app.models.company import Company
from app.services.auth_service import hash_password

settings = get_settings()
init_db(settings.EHS_DATABASE_URL)

import app.database as database
Base.metadata.create_all(bind=database.engine)

db = next(get_db())

# 이미 있는지 확인
existing = db.query(User).filter(User.email == "superadmin@safetyai.kr").first()
if existing:
    print(f"SuperAdmin already exists: {existing.email}")
else:
    # SuperAdmin 전용 회사 생성
    company = Company(name="SafetyAI Platform", business_number="000-00-00000")
    db.add(company)
    db.flush()

    user = User(
        company_id=company.id,
        email="superadmin@safetyai.kr",
        password_hash=hash_password("super123"),
        name="Platform Admin",
        role=UserRole.superadmin.value,
    )
    db.add(user)
    db.commit()
    print("SuperAdmin created!")
    print("  Email: superadmin@safetyai.kr")
    print("  Password: super123")

db.close()
