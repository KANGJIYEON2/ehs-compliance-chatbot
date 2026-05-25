"""
한국철강(주) 데모 데이터 시드 스크립트
──────────────────────────────────────
현실적인 제조업 EHS 데이터를 생성합니다.
- 1개 회사(한국철강), 2개 사업장
- 부서/공정/설비/작업구역 마스터데이터
- 4개 역할 사용자 (admin, field_manager x2, worker x8)
- 사고 40건 (6개월치, 다양한 유형/심각도/상태)
- AI 분석 결과 (캐시)
- 익명 제보 12건
- TBM 세션 20회
- 위험성평가 8건
- 안전수칙 가이드 10건 + 번역 + 교육이수
- 게이미피케이션: 포인트, 퀴즈, 위험도 점수
- 알림 30건
"""

import sys
import uuid
import json
import random
from datetime import datetime, timedelta

sys.path.insert(0, ".")

from app.config import get_settings
from app.database import init_db, get_db, Base
import app.database as database
from app.models import *  # noqa — trigger all model registration
from app.models.company import Company
from app.models.site import Site
from app.models.user import User, UserRole
from app.models.master_data import Department, Process, Equipment, WorkZone
from app.models.incident import Incident, IncidentAttachment
from app.models.ai_analysis import AIAnalysisResult
from app.models.anonymous_report import AnonymousReport
from app.models.safety_guide import SafetyGuide, SafetyGuideTranslation, TrainingRecord
from app.models.gamification import SafetyPoint, SafetyQuiz, QuizResponse, RiskScore
from app.models.tbm import TBMSession, TBMAttendee
from app.models.risk_assessment import RiskAssessment
from app.models.notification import Notification
from app.services.auth_service import hash_password

settings = get_settings()
init_db(settings.EHS_DATABASE_URL)
Base.metadata.create_all(bind=database.engine)

db = next(get_db())


def uid():
    return str(uuid.uuid4())


def dt(days_ago=0, hour=9, minute=0):
    """days_ago일 전의 datetime"""
    return datetime.utcnow() - timedelta(days=days_ago, hours=random.randint(0, 8), minutes=minute)


# ============================================================
# 0. 기존 데모 데이터 정리 (재실행 안전)
# ============================================================
existing_company = db.query(Company).filter(Company.name == "한국철강(주)").first()
if existing_company:
    print("기존 한국철강(주) 데이터를 삭제하고 재생성합니다...")
    # Delete in dependency order
    site_ids = [s.id for s in db.query(Site).filter(Site.company_id == existing_company.id).all()]
    user_ids = [u.id for u in db.query(User).filter(User.company_id == existing_company.id).all()]

    for sid in site_ids:
        # Get incident ids for cascading
        inc_ids = [i.id for i in db.query(Incident).filter(Incident.site_id == sid).all()]
        for iid in inc_ids:
            db.query(AIAnalysisResult).filter(AIAnalysisResult.incident_id == iid).delete()
            db.query(IncidentAttachment).filter(IncidentAttachment.incident_id == iid).delete()
        db.query(Incident).filter(Incident.site_id == sid).delete()

        # TBM
        tbm_ids = [t.id for t in db.query(TBMSession).filter(TBMSession.site_id == sid).all()]
        for tid in tbm_ids:
            db.query(TBMAttendee).filter(TBMAttendee.session_id == tid).delete()
        db.query(TBMSession).filter(TBMSession.site_id == sid).delete()

        # Safety guides
        guide_ids = [g.id for g in db.query(SafetyGuide).filter(SafetyGuide.site_id == sid).all()]
        for gid in guide_ids:
            db.query(SafetyGuideTranslation).filter(SafetyGuideTranslation.guide_id == gid).delete()
            db.query(TrainingRecord).filter(TrainingRecord.guide_id == gid).delete()
        db.query(SafetyGuide).filter(SafetyGuide.site_id == sid).delete()

        # Others
        db.query(AnonymousReport).filter(AnonymousReport.site_id == sid).delete()
        db.query(RiskAssessment).filter(RiskAssessment.site_id == sid).delete()
        db.query(SafetyPoint).filter(SafetyPoint.site_id == sid).delete()
        db.query(SafetyQuiz).filter(SafetyQuiz.site_id == sid).delete()
        db.query(RiskScore).filter(RiskScore.site_id == sid).delete()
        db.query(Department).filter(Department.site_id == sid).delete()
        db.query(Process).filter(Process.site_id == sid).delete()
        db.query(Equipment).filter(Equipment.site_id == sid).delete()
        db.query(WorkZone).filter(WorkZone.site_id == sid).delete()

    for uid_ in user_ids:
        db.query(Notification).filter(Notification.user_id == uid_).delete()
        db.query(QuizResponse).filter(QuizResponse.user_id == uid_).delete()
    db.query(User).filter(User.company_id == existing_company.id).delete()
    db.query(Site).filter(Site.company_id == existing_company.id).delete()
    db.delete(existing_company)
    db.commit()

# Also ensure superadmin exists
superadmin_co = db.query(Company).filter(Company.name == "SafetyAI Platform").first()
if not superadmin_co:
    superadmin_co = Company(id=uid(), name="SafetyAI Platform", business_number="000-00-00000")
    db.add(superadmin_co)
    db.flush()
    sa_user = User(
        id=uid(), company_id=superadmin_co.id,
        email="superadmin@safetyai.kr", password_hash=hash_password("super123"),
        name="Platform Admin", role=UserRole.superadmin.value,
    )
    db.add(sa_user)
    db.commit()
    print("SuperAdmin 생성 완료")

# ============================================================
# 1. 회사 생성
# ============================================================
company = Company(id=uid(), name="한국철강(주)", business_number="123-45-67890")
db.add(company)
db.flush()
print(f"회사 생성: {company.name}")

# ============================================================
# 2. 사업장 (2개)
# ============================================================
site1 = Site(id=uid(), company_id=company.id, name="안산 제1공장", address="경기도 안산시 단원구 산단로 123")
site2 = Site(id=uid(), company_id=company.id, name="인천 제2공장", address="인천광역시 남동구 남동대로 456")
db.add_all([site1, site2])
db.flush()
print(f"사업장 생성: {site1.name}, {site2.name}")

# ============================================================
# 3. 부서 / 공정 / 설비 / 작업구역
# ============================================================
# -- 안산 제1공장 --
depts_s1 = []
for name in ["생산1팀", "생산2팀", "품질관리팀", "설비보전팀", "안전환경팀"]:
    d = Department(id=uid(), site_id=site1.id, name=name)
    depts_s1.append(d)
db.add_all(depts_s1)

procs_s1 = []
proc_names_s1 = ["열간압연", "냉간압연", "산세처리", "도금라인", "절단포장", "원료입고"]
for name in proc_names_s1:
    p = Process(id=uid(), site_id=site1.id, name=name)
    procs_s1.append(p)
db.add_all(procs_s1)

equip_s1 = []
equip_data_s1 = [
    ("열간압연기 #1", 0), ("열간압연기 #2", 0), ("가열로 A", 0), ("가열로 B", 0),
    ("냉간압연기 #1", 1), ("냉간압연기 #2", 1), ("텐션릴", 1),
    ("산세탱크 A", 2), ("산세탱크 B", 2), ("린스장치", 2),
    ("아연도금조", 3), ("컬러코팅기", 3), ("건조로", 3),
    ("슬리팅기", 4), ("레벨러", 4), ("자동포장기", 4),
    ("크레인 #1", 5), ("크레인 #2", 5), ("지게차 A", 5), ("지게차 B", 5),
]
for name, proc_idx in equip_data_s1:
    e = Equipment(id=uid(), site_id=site1.id, process_id=procs_s1[proc_idx].id, name=name)
    equip_s1.append(e)
db.add_all(equip_s1)

zones_s1 = []
for name in ["열연동 1층", "열연동 2층", "냉연동", "산세동", "도금동", "절단포장동", "원료야적장", "완제품 창고", "유틸리티동", "사무동"]:
    z = WorkZone(id=uid(), site_id=site1.id, name=name)
    zones_s1.append(z)
db.add_all(zones_s1)

# -- 인천 제2공장 --
depts_s2 = []
for name in ["생산팀", "품질팀", "보전팀", "안전팀"]:
    d = Department(id=uid(), site_id=site2.id, name=name)
    depts_s2.append(d)
db.add_all(depts_s2)

procs_s2 = []
proc_names_s2 = ["프레스가공", "용접조립", "도장", "검사출하"]
for name in proc_names_s2:
    p = Process(id=uid(), site_id=site2.id, name=name)
    procs_s2.append(p)
db.add_all(procs_s2)

equip_s2 = []
equip_data_s2 = [
    ("유압프레스 #1", 0), ("유압프레스 #2", 0), ("CNC펀칭기", 0),
    ("아크용접기 #1", 1), ("아크용접기 #2", 1), ("스폿용접기", 1), ("로봇용접", 1),
    ("도장부스 A", 2), ("도장부스 B", 2), ("건조오븐", 2),
    ("CMM 측정기", 3), ("포장라인", 3),
]
for name, proc_idx in equip_data_s2:
    e = Equipment(id=uid(), site_id=site2.id, process_id=procs_s2[proc_idx].id, name=name)
    equip_s2.append(e)
db.add_all(equip_s2)

zones_s2 = []
for name in ["프레스동", "용접동", "도장동", "검사동", "자재창고", "완제품 창고"]:
    z = WorkZone(id=uid(), site_id=site2.id, name=name)
    zones_s2.append(z)
db.add_all(zones_s2)

db.flush()
print("마스터데이터 생성 완료")

# ============================================================
# 4. 사용자 (12명)
# ============================================================
pw_admin = hash_password("admin123")
pw_field = hash_password("field123")
pw_worker = hash_password("worker123")

admin_user = User(
    id=uid(), company_id=company.id, email="admin@hankook-steel.kr",
    password_hash=pw_admin, name="이정훈", role=UserRole.admin.value,
)
db.add(admin_user)

# 현장담당자 2명 (각 사업장)
fm1 = User(
    id=uid(), company_id=company.id, site_id=site1.id,
    email="park.jm@hankook-steel.kr", password_hash=pw_field,
    name="박정민", role=UserRole.field_manager.value,
)
fm2 = User(
    id=uid(), company_id=company.id, site_id=site2.id,
    email="choi.sh@hankook-steel.kr", password_hash=pw_field,
    name="최수현", role=UserRole.field_manager.value,
)
db.add_all([fm1, fm2])

# 작업자 8명 (안산 5명, 인천 3명)
workers_s1 = []
worker_data_s1 = [
    ("김민수", "kim.worker@hankook-steel.kr"),
    ("이영호", "lee.yh@hankook-steel.kr"),
    ("Nguyen Van Hung", "nguyen.vh@hankook-steel.kr"),
    ("정대현", "jung.dh@hankook-steel.kr"),
    ("Sok Vanna", "sok.vanna@hankook-steel.kr"),
]
for name, email in worker_data_s1:
    w = User(
        id=uid(), company_id=company.id, site_id=site1.id,
        email=email, password_hash=pw_worker,
        name=name, role=UserRole.worker.value,
    )
    workers_s1.append(w)
db.add_all(workers_s1)

workers_s2 = []
worker_data_s2 = [
    ("한승우", "han.sw@hankook-steel.kr"),
    ("오지훈", "oh.jh@hankook-steel.kr"),
    ("Ram Bahadur", "ram.b@hankook-steel.kr"),
]
for name, email in worker_data_s2:
    w = User(
        id=uid(), company_id=company.id, site_id=site2.id,
        email=email, password_hash=pw_worker,
        name=name, role=UserRole.worker.value,
    )
    workers_s2.append(w)
db.add_all(workers_s2)

db.flush()
all_s1_users = [fm1] + workers_s1
all_s2_users = [fm2] + workers_s2
print(f"사용자 생성: 관리자 1 + 현장담당자 2 + 작업자 8 = 총 11명")

# ============================================================
# 5. 사고/아차사고 40건 (6개월, 현실적 분포)
# ============================================================
incident_templates = [
    # (type, severity, description, cause, action, zone_idx, proc_idx, equip_idx, dept_idx) - all for site1
    ("caught", "serious", "열간압연기 #1 롤 사이에 작업자 왼손 끼임. 안전가드 미작동 상태에서 롤 간격 조정 작업 중 발생.", "안전가드 센서 고장으로 인터록 미작동. 작업자가 센서 고장 인지하고도 수동 작업 진행.", "피재자 응급 이송, 열간압연기 #1 가동 중단, 안전가드 센서 교체 및 인터록 시스템 점검", 0, 0, 0, 0),
    ("fall", "minor", "냉연동 2층 작업발판에서 미끄러져 1.5m 높이에서 추락. 왼쪽 발목 염좌.", "작업발판 위 냉각수 누수로 바닥 미끄러움. 미끄럼 방지 매트 미설치.", "누수 배관 수리, 미끄럼 방지 매트 설치, 안전난간 높이 상향 조정", 2, 1, 4, 0),
    ("chemical", "near_miss", "산세탱크 A 염산 보충 중 호스 연결부 이탈로 염산 소량 비산. 보호구 착용 상태여서 인적 피해 없음.", "호스 클램프 노후화로 고정력 저하. 교체 주기 관리 미흡.", "호스 클램프 전수 교체, 교체 주기를 6개월→3개월로 단축", 3, 2, 7, 3),
    ("fire", "serious", "가열로 B 가스배관 플랜지 부식으로 가스 누출 → 점화. 초기 진화 성공했으나 가열로 외벽 일부 손상.", "가스배관 플랜지 부식 진행 상태에서 정기점검 시 미발견. 배관 비파괴검사 미실시.", "가열로 B 가동 중단, 배관 전체 비파괴검사 실시, 부식 배관 교체", 0, 0, 3, 3),
    ("collision", "near_miss", "원료야적장에서 지게차 B 후진 중 보행자 통행로 침범. 작업자가 사전 회피하여 충돌 방지.", "지게차 후방 카메라 고장 상태. 보행자/차량 통행로 분리 미비.", "지게차 B 후방 카메라 수리, 원료야적장 보행자 통행로 노면 표시 재정비", 6, 5, 18, 1),
    ("electric", "minor", "도금라인 제어반 내부 점검 중 감전. 차단기 투입 상태에서 작업 진행하여 오른팔 감전 화상.", "LOTO(잠금/표찰) 절차 미준수. 당일 긴급 고장 수리로 절차 생략.", "피재자 치료, 전 공정 LOTO 교육 재실시, 긴급수리 시에도 LOTO 의무화", 4, 3, 10, 3),
    ("falling_object", "minor", "완제품 창고 상부 랙에서 코일 제품(약 200kg) 탈락. 작업자 바로 옆에 낙하하여 파편에 의한 찰과상.", "적재 고정 체인 파단. 적재 하중 초과 상태에서 지게차 진동으로 이탈.", "적재 체인 전수 교체, 적재 하중 기준 재설정(80%→60%), 위험구역 출입 통제 강화", 7, 5, 19, 1),
    ("suffocation", "near_miss", "유틸리티동 지하 피트 산소농도 측정 없이 진입 시도. 동료 작업자가 발견하여 제지.", "밀폐공간 작업허가제 미이행. 해당 피트가 밀폐공간 목록에 미등재.", "밀폐공간 전수 재조사 및 목록 갱신, 밀폐공간 출입문 잠금장치 설치", 8, 5, None, 3),
    ("caught", "near_miss", "텐션릴 인근에서 코일 끝단 처리 중 릴 자동 회전. 작업자가 순간적으로 손을 빼서 끼임 방지.", "비상정지 미해제 상태에서 자동복귀 타이머 작동. 작업 전 에너지 차단 미확인.", "텐션릴 자동복귀 타이머 제거, 작업 전 에너지 차단 확인 체크리스트 도입", 2, 1, 6, 0),
    ("other", "near_miss", "열연동 1층 천장 크레인 와이어로프 1가닥 절단 발견. 즉시 사용 중지.", "와이어로프 마모 진행. 월간 점검 시 마모율 측정 기록 부정확.", "크레인 #1 와이어로프 교체, 마모율 측정 디지털 장비 도입, 점검 주기 월→격주", 0, 5, 16, 3),

    ("collision", "minor", "절단포장동에서 슬리팅기 배출 강판에 의한 작업자 손등 절상. 절단면 보호커버 미설치 구간.", "슬리팅 후 절단면이 날카로운 상태로 배출. 보호커버 일부 구간 탈락 후 미보수.", "보호커버 전구간 복원, 절단면 자동 버 제거 장치 검토", 5, 4, 13, 0),
    ("fall", "near_miss", "도금동 탱크 상부 점검 시 난간 없는 구간 발견. 작업자가 보고 후 작업 중단.", "탱크 증설 시 안전난간 미설치 구간 방치. 변경관리(MOC) 절차 누락.", "안전난간 설치 완료, 변경관리(MOC) 절차 재정비 및 교육", 4, 3, 10, 3),
    ("chemical", "minor", "산세처리 공정 중 환기팬 고장으로 염산가스 확산. 작업자 2명 기침/눈따가움 호소.", "환기팬 모터 소손. 예비 환기팬 미확보 상태.", "환기팬 모터 교체, 예비품 확보(2대), 가스 감지기 경보 설정값 재조정", 3, 2, 7, 3),
    ("fire", "near_miss", "원료야적장 인근 용접 불꽃이 폐기물 집하장으로 비산. 자동 소화설비 미설치 구역이었으나 즉시 진화.", "화기작업허가제 미이행. 불꽃비산 방지포 미사용.", "화기작업허가제 준수 교육, 불꽃비산 방지포 현장 비치, 소화기 추가 배치", 6, 5, None, 4),
    ("caught", "minor", "자동포장기 필름 걸림 해제 중 구동롤러에 장갑 끼임. 비상정지 버튼으로 정지하여 경미한 타박상.", "장갑 착용 상태에서 회전체 인근 작업. 회전체 작업 시 장갑 탈착 규정 미인지.", "회전체 인근 장갑 착용 금지 표지 부착, 해당 공정 작업자 안전교육 재실시", 5, 4, 15, 0),

    # 더 최근 사고들 (1-2개월 이내)
    ("fall", "serious", "열연동 2층 유지보수 작업 중 임시 발판 붕괴로 3m 추락. 요추 골절 진단.", "임시 발판 설치 시 구조 검토 미실시. 하중 기준 초과 자재 적재.", "피재자 병원 이송, 임시 발판 사용 금지 → 이동식 비계 의무 사용, 발판 설치 구조 검토 절차 신설", 1, 0, 0, 0),
    ("electric", "near_miss", "냉간압연기 #2 전기실 UPS 배터리 교체 중 단락 스파크 발생. 절연장갑 착용으로 인체 접촉 없음.", "배터리 교체 순서 오류. 양극 먼저 분리해야 하나 음극 먼저 분리.", "전기 작업 표준 작업 절차서(SOP) 개정, 배터리 교체 시 2인 1조 작업 의무화", 2, 1, 5, 3),
    ("collision", "near_miss", "크레인 #2 와이어 하강 중 바닥 작업자와 1m 이내 근접. 신호수 배치 없이 양중 작업 진행.", "신호수 미배치. 양중 작업 시 안전 반경 내 출입 통제 미이행.", "신호수 배치 의무화, 양중 작업 구역 자동 경보 시스템 설치 검토", 0, 5, 17, 1),
    ("other", "minor", "사무동 계단에서 미끄러져 무릎 타박상. 계단 조명 고장 상태.", "계단 조명 2개 중 1개 고장 상태 방치. 시설 관리 점검 누락.", "조명 교체, 비상 조명 추가 설치, 시설 점검 체크리스트에 조명 항목 추가", 9, None, None, 4),
    ("chemical", "serious", "도금라인 아연도금조 청소 작업 중 잔류 화학물질 흡입. 작업자 호흡곤란으로 응급 이송.", "잔류 화학물질 농도 측정 없이 청소 작업 진행. 방독면 대신 방진마스크 착용.", "작업 전 가스 농도 측정 의무화, 화학물질 취급 보호구 기준 재정립, 해당 작업자 건강검진 실시", 4, 3, 10, 0),

    # 인천 제2공장 사고 (15건)
    ("caught", "serious", "유압프레스 #1 금형 교체 중 슬라이드 하강으로 작업자 오른손 끼임. 안전블록 미삽입.", "금형 교체 시 안전블록 삽입 절차 미준수. 시간 압박으로 절차 생략.", "피재자 응급이송, 안전블록 삽입 확인 후에만 슬라이드 작동 가능하도록 인터록 개조", 0, 0, 0, 0),
    ("collision", "minor", "프레스동에서 CNC펀칭기 가공 소재 이탈. 인접 작업자 다리에 충돌하여 타박상.", "소재 고정 지그 마모로 고정력 저하. 점검 기준 미설정.", "지그 교체, 지그 마모도 정기 측정 기준 수립", 0, 0, 2, 0),
    ("fire", "near_miss", "용접동에서 아크용접 중 불꽃이 인근 도료 캔에 비산. 도료 캔 뚜껑이 닫혀 있어 발화 방지.", "가연물 격리 미흡. 용접 작업 반경 내 인화성 물질 관리 부재.", "가연물 격리 구역 설정, 용접 작업 전 가연물 제거 체크리스트 도입", 1, 1, 3, 0),
    ("caught", "near_miss", "스폿용접기 전극 교체 중 실수로 페달 작동. 전극 하강했으나 손이 들어가 있지 않아 무사.", "풋스위치 오작동 방지 커버 미설치. 작업자 실수로 페달 밟음.", "풋스위치 안전커버 설치, 전극 교체 시 전원 차단 절차 의무화", 1, 1, 5, 0),
    ("chemical", "minor", "도장부스 A에서 스프레이건 막힘으로 과압 분사. 도료 미스트 과다 노출.", "스프레이건 필터 막힘. 사용 전 점검 미실시.", "스프레이건 사용 전 점검 의무화, 도장부스 환기 풍속 측정 주기 강화", 2, 2, 7, 0),
    ("fall", "minor", "자재창고 상부 선반(2.5m)에서 자재 꺼내다 이동식 사다리 미끄러짐. 작업자 둔부 타박상.", "이동식 사다리 미끄럼 방지 패드 마모. 사다리 안정성 점검 미실시.", "이동식 사다리 전수 점검 및 교체, 2m 이상 작업 시 안전대 착용 의무화", 4, 3, None, 2),
    ("electric", "near_miss", "로봇용접 셀 티칭 중 안전매트 비활성화 상태 발견. 다른 작업자가 접근 시 로봇 정지 안 됨.", "안전매트 커넥터 접촉 불량. 일상점검 항목에 미포함.", "안전매트 수리 및 일상점검 항목 추가, 로봇 셀 진입 시 인터록 이중화", 1, 1, 6, 2),
    ("falling_object", "minor", "검사동 선반 위 측정 지그(5kg) 낙하. 바닥에서 작업 중이던 작업자 발등에 충돌.", "선반 고정 턱 높이 부족. 진동으로 서서히 이동 후 낙하.", "선반 고정 턱 높이 증가, 중량물 선반 하부 보관 원칙 수립", 3, 3, 10, 1),
    ("other", "near_miss", "완제품 창고 지게차 주행로에 빗물 고임. 지게차 미끄러져 적재물 흔들림.", "배수구 막힘. 우천 시 창고 내 배수 확인 절차 없음.", "배수구 청소, 우천 시 주행로 점검 절차 수립", 5, 3, None, 2),
    ("caught", "minor", "포장라인 컨베이어 벨트 조정 중 벨트와 롤러 사이 장갑 끼임. 비상정지로 경미한 손가락 타박.", "가동 중 벨트 조정 작업. 정지 후 작업해야 하나 생산 일정 압박.", "벨트 조정 시 반드시 정지 후 작업 규정 강화, 일정 압박 시 안전관리자 승인 필요", 3, 3, 11, 0),

    ("collision", "serious", "프레스동 유압프레스 #2 금형 운반 중 크레인 후크에서 금형(300kg) 이탈. 작업자 왼쪽 다리 골절.", "후크 래치 고장 상태에서 양중 작업 진행. 작업 전 장비 점검 미실시.", "크레인 후크 교체, 양중 전 장비 점검 의무화, 중량물 운반 안전구역 설정", 0, 0, 1, 0),
    ("fire", "minor", "건조오븐 내부 도료 잔여물 축적으로 과열 경보. 자동 소화 가동 전 수동 정지.", "오븐 내부 청소 주기(주1회) 미준수. 2주 이상 미청소.", "오븐 청소 기록 관리 체계 수립, 과열 감지 시 자동 차단 로직 추가", 2, 2, 9, 2),
    ("suffocation", "near_miss", "도장동 환기 시스템 고장으로 유기용제 농도 상승. 경보 울려 전원 대피.", "환기팬 벨트 파단. 예비품 미보유.", "환기팬 벨트 교체, 예비품 확보, 유기용제 경보기 설정값 검증", 2, 2, 7, 2),
    ("other", "minor", "CMM 측정기 이동 중 바퀴 고장으로 장비 기울어짐. 작업자가 받치다 허리 근골격계 부담.", "장비 이동용 바퀴 노후. 중량 장비 이동 보조 도구 미비.", "바퀴 교체, 중량 장비 이동 시 전동 운반대 사용 의무화", 3, 3, 10, 1),
    ("fall", "near_miss", "용접동 지붕 보수 작업 중 안전대 미착용 발견. 작업 즉시 중단.", "고소작업 시 안전대 부착 설비 부족. 작업자 안전 인식 부족.", "안전대 부착 설비(생명줄) 설치, 고소작업 특별안전교육 재실시", 1, 1, None, 2),
]

incidents = []
for i, tmpl in enumerate(incident_templates):
    itype, sev, desc, cause, action, zone_idx, proc_idx, equip_idx, dept_idx = tmpl

    # 사업장 구분 (앞 20개 = 안산, 뒤 15개 = 인천)
    if i < 20:
        site = site1
        reporter = random.choice(all_s1_users)
        zones = zones_s1
        procs = procs_s1
        equips = equip_s1
        depts = depts_s1
        assignee = random.choice([fm1, admin_user])
    else:
        site = site2
        reporter = random.choice(all_s2_users)
        zones = zones_s2
        procs = procs_s2
        equips = equip_s2
        depts = depts_s2
        assignee = random.choice([fm2, admin_user])
        # 인천 사고의 인덱스 보정
        zone_idx = min(zone_idx, len(zones) - 1)
        if proc_idx is not None:
            proc_idx = min(proc_idx, len(procs) - 1)
        if equip_idx is not None:
            equip_idx = min(equip_idx, len(equips) - 1)
        dept_idx = min(dept_idx, len(depts) - 1)

    # 시간 분포: 6개월에 걸쳐 (최신이 인덱스 높을수록 최근)
    days_ago = max(1, 180 - (i * 4) + random.randint(-3, 3))

    # 상태 분포
    if days_ago > 120:
        status = random.choice(["resolved", "monitoring"])
    elif days_ago > 60:
        status = random.choice(["resolved", "investigating", "monitoring"])
    elif days_ago > 20:
        status = random.choice(["investigating", "resolved", "reported"])
    else:
        status = random.choice(["reported", "investigating"])

    inc = Incident(
        id=uid(),
        site_id=site.id,
        reporter_id=reporter.id,
        incident_type=itype,
        severity=sev,
        occurred_at=dt(days_ago),
        work_zone_id=zones[zone_idx].id if zone_idx is not None else None,
        process_id=procs[proc_idx].id if proc_idx is not None else None,
        equipment_id=equips[equip_idx].id if equip_idx is not None else None,
        department_id=depts[dept_idx].id if dept_idx is not None else None,
        description=desc,
        cause_estimate=cause,
        action_taken=action if status in ("resolved", "monitoring") else None,
        status=status,
        assignee_id=assignee.id if status != "reported" else None,
        assignee_name=assignee.name if status != "reported" else None,
        due_date=dt(days_ago - 7) if status in ("investigating",) else None,
        created_at=dt(days_ago),
        updated_at=dt(max(1, days_ago - random.randint(0, 5))),
    )
    incidents.append(inc)

db.add_all(incidents)
db.flush()
print(f"사고/아차사고 {len(incidents)}건 생성")

# ============================================================
# 6. AI 분석 결과 (사고 10건에 대해)
# ============================================================
ai_results = []
for inc in incidents[:10]:
    # analysis
    ai_results.append(AIAnalysisResult(
        id=uid(), incident_id=inc.id, analysis_type="analysis",
        result_json=json.dumps({
            "risk_level": random.choice(["high", "medium", "critical"]),
            "root_cause": inc.cause_estimate,
            "contributing_factors": [
                "안전 교육 미흡", "점검 절차 미준수", "장비 노후화"
            ][:random.randint(1, 3)],
            "immediate_actions": ["작업 중단", "현장 보존", "피재자 응급조치"],
            "long_term_recommendations": [
                "정기점검 주기 강화",
                "안전장비 교체 및 업그레이드",
                "작업 절차 개정 및 교육 강화",
                "안전 문화 개선 프로그램 도입"
            ][:random.randint(2, 4)],
        }, ensure_ascii=False),
        created_at=dt(max(1, (datetime.utcnow() - inc.created_at).days - 1)),
    ))
    # checklist
    ai_results.append(AIAnalysisResult(
        id=uid(), incident_id=inc.id, analysis_type="checklist",
        result_json=json.dumps({
            "items": [
                {"task": "사고 현장 보존 및 사진 촬영", "priority": "high", "completed": True},
                {"task": "목격자 진술 확보", "priority": "high", "completed": True},
                {"task": "관련 장비 점검 기록 확인", "priority": "medium", "completed": random.choice([True, False])},
                {"task": "유사 사고 이력 조회", "priority": "medium", "completed": False},
                {"task": "재발 방지 대책 수립", "priority": "high", "completed": False},
                {"task": "관련 작업자 안전교육 실시", "priority": "medium", "completed": False},
                {"task": "안전보건관리 규정 개정 검토", "priority": "low", "completed": False},
            ]
        }, ensure_ascii=False),
        created_at=dt(max(1, (datetime.utcnow() - inc.created_at).days - 1)),
    ))
    # legal basis
    ai_results.append(AIAnalysisResult(
        id=uid(), incident_id=inc.id, analysis_type="legal_basis",
        result_json=json.dumps({
            "related_laws": [
                {
                    "law_name": "산업안전보건법",
                    "article": "제38조 (안전조치)",
                    "summary": "사업주는 기계·기구, 그 밖의 설비에 의한 위험을 예방하기 위하여 필요한 조치를 하여야 한다.",
                    "penalty": "5년 이하의 징역 또는 5천만원 이하의 벌금"
                },
                {
                    "law_name": "중대재해처벌법",
                    "article": "제4조 (사업주와 경영책임자등의 안전 및 보건 확보의무)",
                    "summary": "사업주 또는 경영책임자등은 사업주나 법인 또는 기관이 실질적으로 지배·운영·관리하는 사업 또는 사업장에서 종사자의 안전·보건상 유해 또는 위험을 방지하기 위하여 그 사업 또는 사업장의 특성 및 규모 등을 고려하여 재해예방에 필요한 안전보건관리체계를 구축하고 이행에 관한 조치를 하여야 한다.",
                    "penalty": "1년 이상의 징역 또는 10억원 이하의 벌금"
                },
            ],
            "employer_obligations": [
                "위험 기계·기구에 대한 방호조치 의무",
                "정기 안전점검 실시 의무",
                "안전보건교육 실시 의무",
                "작업환경측정 및 건강진단 실시 의무"
            ]
        }, ensure_ascii=False),
        created_at=dt(max(1, (datetime.utcnow() - inc.created_at).days - 1)),
    ))

db.add_all(ai_results)
db.flush()
print(f"AI 분석 결과 {len(ai_results)}건 생성 (사고 10건 x 3유형)")

# ============================================================
# 7. 익명 제보 12건
# ============================================================
anon_templates = [
    ("안산", site1, "열연동 1층 비상구 앞에 자재가 쌓여 있어서 대피 시 통행이 불가능합니다. 지난 주부터 계속 방치되어 있습니다.", "critical", "fire", "열연동 1층 비상구 앞"),
    ("안산", site1, "산세동에서 일하는데 환기가 잘 안 됩니다. 마스크를 써도 냄새가 심하고 두통이 생깁니다.", "warning", "chemical", "산세동"),
    ("안산", site1, "지게차 B 브레이크가 밀리는 것 같습니다. 운전자한테 얘기했는데 그냥 타라고 합니다.", "critical", "collision", "원료야적장"),
    ("안산", site1, "안전화가 3개월 전에 신청했는데 아직 안 왔습니다. 운동화 신고 작업하고 있습니다.", "warning", "other", None),
    ("안산", site1, "야간 근무 시 조명이 너무 어두워서 위험합니다. 특히 냉연동 통로 쪽이 심합니다.", "improvement", "fall", "냉연동 통로"),
    ("안산", site1, "도금라인에서 야간에 1명이 혼자 작업하는 경우가 있습니다. 위험한 공정인데 2인 1조 원칙이 안 지켜지고 있습니다.", "critical", "electric", "도금동"),
    ("인천", site2, "프레스 금형 교체 시 안전블록을 안 쓰는 사람이 많습니다. 시간이 오래 걸린다는 이유로요.", "critical", "caught", "프레스동"),
    ("인천", site2, "용접동 환기 팬이 3대 중 1대밖에 안 돌아갑니다. 수리 요청한 지 2주 넘었습니다.", "warning", "suffocation", "용접동"),
    ("인천", site2, "도장부스에서 쓰는 유기용제 MSDS가 없습니다. 어떤 화학물질인지 모르고 쓰고 있습니다.", "warning", "chemical", "도장동"),
    ("인천", site2, "완제품 창고 지게차 통로에 빗물이 자주 고입니다. 미끄러운데 아무런 조치가 없습니다.", "improvement", "fall", "완제품 창고"),
    ("인천", site2, "신입 작업자가 들어왔는데 안전교육 없이 바로 프레스 작업에 투입됐습니다.", "critical", "caught", "프레스동"),
    ("인천", site2, "건조오븐 온도계가 고장 나서 정확한 온도 확인이 안 됩니다. 과열 사고 날까 봐 걱정됩니다.", "warning", "fire", "도장동"),
]

anon_reports = []
for i, (_, site, content, risk, cat, loc) in enumerate(anon_templates):
    days_ago = 90 - (i * 7) + random.randint(-2, 2)
    status = "resolved" if days_ago > 60 else ("reviewing" if days_ago > 30 else "received")
    report = AnonymousReport(
        id=uid(), site_id=site.id,
        content=content, location_hint=loc,
        risk_level=risk, ai_category=cat,
        status=status,
        admin_response="확인하여 조치 완료했습니다. 제보 감사합니다." if status == "resolved" else (
            "확인 중입니다. 빠른 시일 내 조치하겠습니다." if status == "reviewing" else None
        ),
        created_at=dt(days_ago),
        resolved_at=dt(days_ago - 5) if status == "resolved" else None,
    )
    anon_reports.append(report)

db.add_all(anon_reports)
db.flush()
print(f"익명 제보 {len(anon_reports)}건 생성")

# ============================================================
# 8. TBM 세션 20회 (각 사업장 10회)
# ============================================================
tbm_sessions = []
tbm_agenda_templates = [
    {
        "items": [
            {"topic": "전일 사고/아차사고 공유", "duration": 5, "presenter": "현장반장"},
            {"topic": "금일 작업 내용 및 위험요인 확인", "duration": 10, "presenter": "작업반장"},
            {"topic": "개인보호구 착용 상태 점검", "duration": 5, "presenter": "안전담당"},
            {"topic": "기상 정보 및 주의사항", "duration": 3, "presenter": "현장반장"},
            {"topic": "질의응답 및 안전 구호", "duration": 2, "presenter": "전원"},
        ],
        "safety_reminders": ["안전모/안전화 착용 필수", "중량물 취급 시 2인 1조", "이상 발견 시 즉시 보고"]
    },
    {
        "items": [
            {"topic": "안전사고 사례 공유 (타 사업장)", "duration": 5, "presenter": "안전담당"},
            {"topic": "금일 중점 관리 공정 안내", "duration": 8, "presenter": "작업반장"},
            {"topic": "화기 작업 시 주의사항", "duration": 5, "presenter": "안전담당"},
            {"topic": "비상 대피 경로 확인", "duration": 3, "presenter": "현장반장"},
            {"topic": "건강 상태 확인 및 질의", "duration": 4, "presenter": "전원"},
        ],
        "safety_reminders": ["화기 작업 시 소화기 비치", "비상구 위치 확인", "체온 이상 시 보고"]
    },
]

for site, creator, proc_names, worker_names in [
    (site1, fm1, proc_names_s1, [w.name for w in workers_s1]),
    (site2, fm2, proc_names_s2, [w.name for w in workers_s2]),
]:
    for j in range(10):
        days_ago = j * 7 + random.randint(0, 3)  # 주 1회
        session = TBMSession(
            id=uid(), site_id=site.id, created_by=creator.id,
            date=(datetime.utcnow() - timedelta(days=days_ago)).strftime("%Y-%m-%d"),
            process_name=random.choice(proc_names),
            agenda=json.dumps(random.choice(tbm_agenda_templates), ensure_ascii=False),
            weather_info=json.dumps({
                "temp": random.randint(5, 32),
                "condition": random.choice(["맑음", "흐림", "비", "눈", "안개"]),
                "humidity": random.randint(30, 85),
                "wind": f"{random.uniform(0.5, 8.0):.1f}m/s",
                "precaution": random.choice([
                    "고온 주의 — 충분한 수분 섭취",
                    "결빙 주의 — 미끄럼 방지 조치",
                    "강풍 주의 — 양중 작업 주의",
                    "안개 주의 — 시야 확보",
                    "특이사항 없음",
                ])
            }, ensure_ascii=False),
            created_at=dt(days_ago),
        )
        db.add(session)
        db.flush()

        # 참석자 (3~6명)
        attendee_names = random.sample(worker_names, min(len(worker_names), random.randint(3, 6)))
        attendee_names.append(creator.name)
        for name in attendee_names:
            att = TBMAttendee(
                id=uid(), session_id=session.id, user_name=name,
                acknowledged=random.random() > 0.1,
                acknowledged_at=dt(days_ago) if random.random() > 0.1 else None,
            )
            db.add(att)

        tbm_sessions.append(session)

db.flush()
print(f"TBM 세션 {len(tbm_sessions)}회 생성")

# ============================================================
# 9. 위험성평가 8건
# ============================================================
ra_templates = [
    ("열간압연", "열간압연기 롤 간격 조정", "가열된 강재를 열간압연기에 통과시켜 두께를 조정하는 작업. 롤 간격 수동 조정 및 소재 투입 보조 포함.", "high"),
    ("냉간압연", "냉간압연기 코일 장입/취출", "냉간압연기에 코일을 장입하고 취출하는 작업. 크레인 사용 및 텐션릴 조작 포함.", "medium"),
    ("산세처리", "산세탱크 약품 보충", "산세탱크에 염산을 보충하는 작업. 호스 연결 및 밸브 조작, 농도 측정 포함.", "high"),
    ("도금라인", "아연도금조 청소", "도금조 내부 슬러지 제거 및 청소 작업. 밀폐공간 작업에 해당하며 잔류 화학물질 노출 위험.", "high"),
    ("프레스가공", "유압프레스 금형 교체", "유압프레스의 상/하 금형을 교체하는 작업. 슬라이드 하강 방지를 위한 안전블록 삽입 필요.", "high"),
    ("용접조립", "아크용접 조립", "부품 조립을 위한 아크용접 작업. 용접 흄, 자외선, 화재 위험 포함.", "medium"),
    ("도장", "스프레이 도장", "스프레이건을 이용한 수동 도장 작업. 유기용제 증기 노출 및 화재 위험.", "medium"),
    ("절단포장", "슬리팅 작업", "코일을 지정 폭으로 슬리팅하는 작업. 절단면에 의한 베임 위험 및 소음 노출.", "low"),
]

risk_assessments = []
for i, (proc, task, desc, level) in enumerate(ra_templates):
    site = site1 if i < 4 else site2
    creator = fm1 if i < 4 else fm2

    hazards = json.dumps([
        {"hazard": "기계적 위험 — 끼임, 절단, 충돌", "source": "회전체/이동부", "affected": "작업자 상지/하지"},
        {"hazard": "화학적 위험 — 유해물질 노출", "source": "공정 물질", "affected": "호흡기/피부"},
        {"hazard": "물리적 위험 — 소음, 진동, 고온", "source": "장비 가동", "affected": "청력/체온조절"},
    ][:random.randint(1, 3)], ensure_ascii=False)

    risk_matrix = json.dumps([
        {"hazard": "끼임", "likelihood": random.randint(2, 4), "severity": random.randint(3, 5), "risk_score": random.randint(8, 20), "risk_grade": level},
        {"hazard": "화학물질 노출", "likelihood": random.randint(1, 3), "severity": random.randint(2, 4), "risk_score": random.randint(4, 12), "risk_grade": "medium" if level != "low" else "low"},
    ], ensure_ascii=False)

    measures = json.dumps([
        {"type": "공학적 대책", "description": "안전가드 설치, 인터록 장치, 국소배기장치"},
        {"type": "관리적 대책", "description": "작업 절차서 정비, 안전교육, LOTO 절차"},
        {"type": "개인보호구", "description": "안전모, 보안경, 방진마스크, 안전장갑, 안전화"},
    ], ensure_ascii=False)

    legal = json.dumps([
        {"law": "산업안전보건법 제38조", "title": "안전조치", "relevance": "기계·기구 위험 예방 조치 의무"},
        {"law": "산업안전보건기준에 관한 규칙 제87조", "title": "원재료 등의 위험 방지", "relevance": "화학물질 취급 안전 조치"},
    ], ensure_ascii=False)

    days_ago = 60 - (i * 7)
    status = "approved" if days_ago > 40 else ("reviewed" if days_ago > 20 else "draft")

    ra = RiskAssessment(
        id=uid(), site_id=site.id, created_by=creator.id,
        process_name=proc, task_name=task, task_description=desc,
        hazards=hazards, risk_matrix=risk_matrix, measures=measures, legal_basis=legal,
        risk_level=level, status=status,
        created_at=dt(days_ago), updated_at=dt(max(1, days_ago - 3)),
    )
    risk_assessments.append(ra)

db.add_all(risk_assessments)
db.flush()
print(f"위험성평가 {len(risk_assessments)}건 생성")

# ============================================================
# 10. 안전수칙 가이드 10건 + 번역 + 교육이수
# ============================================================
guide_data = [
    ("equipment", equip_s1[0], "열간압연기 안전수칙",
     "1. 작업 전 안전가드 및 인터록 장치 정상 작동 확인\n2. 롤 간격 조정 시 반드시 장비 정지 후 작업\n3. 고온 소재 접근 시 내열 보호구(내열장갑, 보안면) 착용\n4. 비상정지 버튼 위치 숙지 및 작동 확인\n5. 소재 투입 시 협착 위험 구역 진입 금지\n6. 이상 소음/진동 발생 시 즉시 작업 중단 및 보고"),
    ("equipment", equip_s1[7], "산세탱크 안전수칙",
     "1. 방독면(산성가스용) 및 내화학 보호복 착용 필수\n2. 약품 보충 시 호스 연결부 2중 확인\n3. 탱크 내부 진입 시 밀폐공간 작업 허가 필수\n4. 비상 세안/세척 설비 위치 및 작동 확인\n5. 염산 취급 시 물과 접촉 주의 (발열 반응)\n6. MSDS 비치 확인 및 내용 숙지"),
    ("work_zone", zones_s1[6], "원료야적장 안전수칙",
     "1. 지게차 운행 시 보행자 통행로 절대 진입 금지\n2. 크레인 양중 작업 시 안전 반경 내 출입 통제\n3. 적재물 높이 제한 준수 (3단 이하)\n4. 야적장 내 보행 시 지정 통로 사용\n5. 우천 시 미끄럼 주의, 속도 제한(10km/h)\n6. 야간 작업 시 조끼 및 경광봉 사용"),
    ("equipment", equip_s1[10], "아연도금조 안전수칙",
     "1. 도금조 접근 시 내화학 보호구 풀세트 착용\n2. 아연 흄 흡입 방지를 위한 호흡보호구 착용\n3. 고온 아연(450°C) 비산 주의 — 내열 보호복 착용\n4. 도금조 청소 시 잔류 화학물질 농도 측정 후 작업\n5. 비상 시 샤워/세안 설비 사용법 숙지\n6. 화상 발생 시 즉시 냉수 처치 및 보고"),
    ("work_zone", zones_s1[0], "열연동 1층 안전수칙",
     "1. 입장 시 안전모, 안전화, 보안경, 귀마개 착용 필수\n2. 바닥 고온 구역 표시 확인 — 내열 안전화 착용\n3. 크레인 작업 구역 진입 시 신호수 확인 후 통과\n4. 비상구 위치 및 대피 경로 숙지 (분기 1회 훈련)\n5. 소화기/소화전 위치 숙지\n6. 이상 발견 시 즉시 현장반장에게 보고"),
    ("equipment", equip_s2[0], "유압프레스 안전수칙",
     "1. 금형 교체 시 반드시 안전블록 삽입 후 작업\n2. 양수 조작 방식 — 한 손 조작 절대 금지\n3. 작업 전 비상정지 장치 작동 확인\n4. 소재 투입/취출 시 핸드 인 다이(Hand in Die) 금지\n5. 금형 주변 이물질 제거 후 프레스 작동\n6. 이상 소음/진동 감지 시 즉시 정지 및 보고"),
    ("equipment", equip_s2[3], "아크용접기 안전수칙",
     "1. 용접 마스크(차광도 #10 이상) 및 가죽장갑 착용\n2. 용접 흄 차단을 위한 국소배기장치 가동 확인\n3. 가연물 반경 11m 이내 제거 또는 불연 커버 설치\n4. 밀폐 공간 용접 시 산소농도 측정 및 환기\n5. 용접 후 1시간 이상 화재 감시\n6. 케이블 손상 확인 — 감전 예방"),
    ("work_zone", zones_s2[1], "용접동 안전수칙",
     "1. 환기 시스템 정상 가동 확인 후 입장\n2. 소화기/소화전 위치 숙지 (입구, 중앙, 후문 3곳)\n3. 용접 작업 구역 파티션으로 격리\n4. 바닥 물기 제거 — 감전 예방\n5. 고소 작업 시 안전대 착용 및 부착 설비 확인\n6. 비상구 2곳 위치 확인 (정문, 후문)"),
    ("equipment", equip_s2[7], "도장부스 안전수칙",
     "1. 방독면(유기용제용) 및 내화학 보호복 착용\n2. 도장부스 환기팬 정상 가동 확인 (풍속 0.4m/s 이상)\n3. 도장 전 정전기 방지 조치 (접지, 정전기 방지 의류)\n4. 유기용제 MSDS 확인 및 비치\n5. 도장 중 화기 사용 절대 금지\n6. 도장 후 환기 시간 준수 (최소 30분)"),
    ("work_zone", zones_s2[4], "자재창고 안전수칙",
     "1. 2m 이상 높이 자재 꺼낼 시 안전사다리/리프트 사용\n2. 통로 적재물 방치 금지 — 보행 통로 확보\n3. 지게차 운행 시 보행자 우선 원칙\n4. 중량물(20kg 이상) 취급 시 보조 장비 사용\n5. 화재 위험 자재 격리 보관\n6. FIFO(선입선출) 원칙 준수"),
]

guides = []
for target_type, target_obj, title, content in guide_data:
    site = site1 if target_obj.site_id == site1.id else site2
    g = SafetyGuide(
        id=uid(), site_id=site.id,
        target_type=target_type,
        target_id=target_obj.id,
        target_name=title,
        content_ko=content,
        created_at=dt(random.randint(30, 90)),
    )
    guides.append(g)
db.add_all(guides)
db.flush()

# 번역 (일부 가이드에 베트남어/영어 번역 추가)
translations = []
vi_translations = {
    0: "1. Trước khi làm việc, kiểm tra bộ phận bảo vệ an toàn và thiết bị khóa liên động\n2. Khi điều chỉnh khoảng cách con lăn, phải dừng thiết bị\n3. Khi tiếp cận vật liệu nóng, đeo găng tay chống nhiệt và mặt nạ bảo hộ\n4. Nắm rõ vị trí nút dừng khẩn cấp\n5. Cấm vào khu vực nguy hiểm kẹp khi nạp vật liệu\n6. Dừng ngay và báo cáo khi có tiếng ồn/rung bất thường",
    1: "1. Bắt buộc đeo mặt nạ phòng độc và mặc đồ bảo hộ chống hóa chất\n2. Kiểm tra kết nối ống 2 lần khi bổ sung hóa chất\n3. Khi vào bên trong bể, phải có giấy phép làm việc không gian kín\n4. Xác nhận vị trí và hoạt động của thiết bị rửa mắt khẩn cấp\n5. Cẩn thận khi axit tiếp xúc với nước (phản ứng tỏa nhiệt)\n6. Kiểm tra MSDS và nắm rõ nội dung",
    5: "1. Khi thay khuôn, phải đặt khối an toàn trước khi làm việc\n2. Vận hành bằng hai tay — tuyệt đối cấm vận hành một tay\n3. Kiểm tra thiết bị dừng khẩn cấp trước khi làm việc\n4. Cấm đưa tay vào khuôn khi nạp/lấy vật liệu\n5. Loại bỏ vật lạ xung quanh khuôn trước khi vận hành\n6. Dừng ngay và báo cáo khi phát hiện tiếng ồn/rung bất thường",
}
en_translations = {
    0: "1. Before work, confirm safety guards and interlock devices are functioning\n2. Equipment must be stopped for roll gap adjustment\n3. Wear heat-resistant PPE when approaching hot materials\n4. Know the location of emergency stop buttons\n5. No entry to pinch-point danger zones during material feeding\n6. Stop work immediately and report any abnormal noise/vibration",
    2: "1. Never enter forklift travel paths as a pedestrian\n2. Maintain safety zone exclusion during crane lifting operations\n3. Comply with stacking height limits (3 tiers max)\n4. Use designated walking paths within the yard\n5. Caution on wet surfaces — speed limit 10km/h in rain\n6. Wear reflective vest and use light batons for night work",
    5: "1. Safety block must be inserted before die change work\n2. Two-hand operation only — single-hand operation strictly prohibited\n3. Verify emergency stop device before starting work\n4. No hand-in-die during material loading/unloading\n5. Remove foreign objects around the die before press operation\n6. Stop immediately and report abnormal noise/vibration",
}

for idx, content_vi in vi_translations.items():
    t = SafetyGuideTranslation(
        id=uid(), guide_id=guides[idx].id, language="vi",
        content=content_vi, translated_at=dt(random.randint(20, 80)),
    )
    translations.append(t)

for idx, content_en in en_translations.items():
    t = SafetyGuideTranslation(
        id=uid(), guide_id=guides[idx].id, language="en",
        content=content_en, translated_at=dt(random.randint(20, 80)),
    )
    translations.append(t)

db.add_all(translations)

# 교육 이수 기록
training_records = []
for guide in guides[:6]:
    for _ in range(random.randint(2, 5)):
        lang = random.choice(["ko", "vi", "en", "ko", "ko"])  # 한국어 가중치
        tr = TrainingRecord(
            id=uid(), guide_id=guide.id, language=lang,
            acknowledged_at=dt(random.randint(5, 60)),
        )
        training_records.append(tr)

db.add_all(training_records)
db.flush()
print(f"안전수칙 가이드 {len(guides)}건 + 번역 {len(translations)}건 + 교육이수 {len(training_records)}건")

# ============================================================
# 11. 게이미피케이션 (포인트, 퀴즈, 위험도 점수)
# ============================================================
# 포인트
points = []
point_reasons = [
    ("report", 50), ("report", 50), ("tbm", 30), ("tbm", 30),
    ("quiz", 20), ("quiz", 20), ("quiz", 20),
    ("qr_check", 10), ("qr_check", 10),
    ("no_accident", 100),
]
all_workers = workers_s1 + workers_s2
for worker in all_workers:
    site = site1 if worker in workers_s1 else site2
    num_entries = random.randint(5, 15)
    for _ in range(num_entries):
        reason, pts = random.choice(point_reasons)
        p = SafetyPoint(
            id=uid(), user_id=worker.id, site_id=site.id,
            points=pts, reason=reason,
            created_at=dt(random.randint(1, 90)),
        )
        points.append(p)

db.add_all(points)

# 퀴즈
quizzes = []
quiz_data = [
    ("산업안전보건법에서 정하는 안전모 착용 의무 장소로 올바른 것은?",
     '["사무실 내부", "물체가 떨어지거나 날아올 위험이 있는 작업장", "구내 식당", "주차장"]',
     1, "산업안전보건기준에 관한 규칙 제32조에 따라 물체가 떨어지거나 날아올 위험이 있는 작업장에서는 안전모를 착용하여야 합니다."),
    ("LOTO(Lockout/Tagout) 절차의 주요 목적은?",
     '["생산 효율 향상", "에너지원 차단으로 작업자 안전 확보", "장비 수명 연장", "품질 관리"]',
     1, "LOTO는 기계 정비/수리 시 에너지원(전기, 유압, 공압 등)을 차단하고 잠금/표찰을 부착하여 예기치 않은 기동을 방지하는 절차입니다."),
    ("밀폐공간 작업 시 산소농도의 적정 범위는?",
     '["16% 이상", "18% 이상 23.5% 미만", "21% 정확히", "25% 이상"]',
     1, "산업안전보건기준에 관한 규칙 제618조에 따라 밀폐공간의 적정 산소농도는 18% 이상 23.5% 미만입니다."),
    ("화재 발생 시 소화기 사용법으로 올바른 순서는?",
     '["조준→안전핀→손잡이→빗자루", "안전핀 제거→노즐 조준→손잡이 압착→빗자루 쓸듯이", "손잡이→안전핀→조준→분사", "노즐→손잡이→안전핀→분사"]',
     1, "소화기 사용법: 안전핀 제거 → 노즐을 불쪽으로 조준 → 손잡이를 꽉 쥐고 → 빗자루 쓸듯이 좌우로 분사합니다."),
    ("고소작업(2m 이상)에서 가장 중요한 안전조치는?",
     '["작업 속도 높이기", "안전대 착용 및 부착설비 사용", "밝은 색 작업복 착용", "동료에게 알리기"]',
     1, "산업안전보건기준에 관한 규칙 제44조에 따라 높이 2m 이상의 장소에서 작업 시 안전대를 착용하고 안전대 부착설비를 사용하여야 합니다."),
    ("유해화학물질의 MSDS(물질안전보건자료)에 포함되어야 하는 정보가 아닌 것은?",
     '["제품명 및 회사 정보", "유해·위험성", "제품 가격 정보", "응급조치 요령"]',
     2, "MSDS에는 제품명, 유해위험성, 구성성분, 응급조치, 취급 및 저장방법 등 16개 항목이 포함되며, 가격 정보는 포함되지 않습니다."),
    ("크레인 양중 작업 시 신호수가 반드시 필요한 경우는?",
     '["1톤 미만 하물", "운전자가 하물을 볼 수 없을 때", "맑은 날씨일 때", "작업 시간 중"]',
     1, "산업안전보건기준에 관한 규칙 제38조에 따라 운전자가 하물을 볼 수 없는 경우 신호수를 배치하여야 합니다."),
    ("감전 사고 발생 시 가장 먼저 해야 할 조치는?",
     '["심폐소생술", "119 신고", "전원 차단", "물을 끼얹기"]',
     2, "감전 사고 시 가장 먼저 전원을 차단하여 추가 감전을 방지해야 합니다. 전원 차단이 불가능한 경우 절연물을 이용하여 피해자를 분리합니다."),
    ("소음성 난청을 예방하기 위한 청력보호구 착용 기준은?",
     '["80dB 이상", "85dB 이상(1일 8시간 기준)", "90dB 이상", "95dB 이상"]',
     1, "산업안전보건기준에 관한 규칙에 따라 1일 8시간 작업 기준 85dB 이상의 소음에 노출되는 작업장에서는 청력보호구를 착용해야 합니다."),
    ("지게차 운전 시 안전수칙으로 올바르지 않은 것은?",
     '["전방 시야 확보 상태에서 운전", "화물 적재 시 마스트를 뒤로 기울여 운반", "사람을 포크 위에 태워 작업", "경사로에서는 전진으로 오르고 후진으로 내려감"]',
     2, "지게차 포크 위에 사람을 태우는 것은 절대 금지입니다. 고소 작업이 필요한 경우 전용 작업대를 사용해야 합니다."),
]

for i, (question, options, correct, explanation) in enumerate(quiz_data):
    site = site1 if i < 6 else site2
    q = SafetyQuiz(
        id=uid(), site_id=site.id,
        question=question, options=options,
        correct_index=correct, explanation=explanation,
        generated_at=dt(i * 3 + random.randint(0, 2)),
    )
    quizzes.append(q)

db.add_all(quizzes)
db.flush()

# 퀴즈 응답
responses = []
for worker in all_workers:
    answered_count = random.randint(3, 8)
    available_quizzes = [q for q in quizzes if q.site_id == (site1.id if worker in workers_s1 else site2.id)]
    for quiz in random.sample(available_quizzes, min(answered_count, len(available_quizzes))):
        selected = quiz.correct_index if random.random() > 0.3 else random.randint(0, 3)
        r = QuizResponse(
            id=uid(), quiz_id=quiz.id, user_id=worker.id,
            selected_index=selected, is_correct=(selected == quiz.correct_index),
            answered_at=dt(random.randint(1, 60)),
        )
        responses.append(r)

db.add_all(responses)

# 위험도 점수
risk_scores = []
for proc in procs_s1:
    rs = RiskScore(
        id=uid(), site_id=site1.id,
        target_type="process", target_id=proc.id, target_name=proc.name,
        score=random.randint(25, 85),
        factors=json.dumps({
            "incident_count": random.randint(0, 8),
            "severity_weight": round(random.uniform(1.0, 4.0), 1),
            "days_since_last": random.randint(5, 120),
            "overdue_actions": random.randint(0, 3),
            "near_miss_ratio": round(random.uniform(0.1, 0.6), 2),
        }, ensure_ascii=False),
        calculated_at=dt(random.randint(1, 7)),
    )
    risk_scores.append(rs)

for proc in procs_s2:
    rs = RiskScore(
        id=uid(), site_id=site2.id,
        target_type="process", target_id=proc.id, target_name=proc.name,
        score=random.randint(30, 78),
        factors=json.dumps({
            "incident_count": random.randint(0, 6),
            "severity_weight": round(random.uniform(1.0, 3.5), 1),
            "days_since_last": random.randint(10, 90),
            "overdue_actions": random.randint(0, 2),
            "near_miss_ratio": round(random.uniform(0.15, 0.5), 2),
        }, ensure_ascii=False),
        calculated_at=dt(random.randint(1, 7)),
    )
    risk_scores.append(rs)

db.add_all(risk_scores)
db.flush()
print(f"포인트 {len(points)}건 + 퀴즈 {len(quizzes)}건 + 응답 {len(responses)}건 + 위험도 {len(risk_scores)}건")

# ============================================================
# 12. 알림 30건
# ============================================================
notifications = []
notif_templates = [
    ("incident_new", "새 사고 보고", "열연동 1층에서 끼임 사고가 보고되었습니다.", "/incidents/"),
    ("incident_assigned", "사고 담당 배정", "열간압연기 #1 끼임 사고 조치 담당자로 배정되었습니다.", "/incidents/"),
    ("incident_overdue", "조치 기한 초과", "냉연동 추락 사고의 조치 기한이 3일 초과되었습니다. 빠른 조치 바랍니다.", "/incidents/"),
    ("report_new", "새 익명 제보", "안산 제1공장에 새로운 익명 제보가 접수되었습니다.", "/anonymous-reports"),
    ("tbm_reminder", "TBM 참석 알림", "오늘 오전 8:00 열간압연 공정 TBM이 예정되어 있습니다.", "/tbm"),
    ("incident_new", "아차사고 보고", "산세동에서 화학물질 비산 아차사고가 보고되었습니다.", "/incidents/"),
    ("incident_assigned", "조치 요청", "유틸리티동 밀폐공간 아차사고 조치 담당자로 배정되었습니다.", "/incidents/"),
    ("incident_overdue", "기한 초과 경고", "도금라인 감전 사고 조치 기한이 초과되었습니다.", "/incidents/"),
    ("report_new", "위험 제보", "인천 제2공장에 Critical 등급 제보가 접수되었습니다.", "/anonymous-reports"),
    ("tbm_reminder", "TBM 알림", "내일 오전 프레스가공 공정 TBM 참석 바랍니다.", "/tbm"),
]

target_users = [admin_user, fm1, fm2]
for i in range(30):
    tmpl = notif_templates[i % len(notif_templates)]
    user = target_users[i % len(target_users)]
    days_ago = max(0, 30 - i)
    n = Notification(
        id=uid(), user_id=user.id,
        type=tmpl[0], title=tmpl[1], message=tmpl[2], link=tmpl[3],
        is_read=days_ago > 7,
        created_at=dt(days_ago),
    )
    notifications.append(n)

db.add_all(notifications)
db.commit()
print(f"알림 {len(notifications)}건 생성")

# ============================================================
# DONE
# ============================================================
print("\n" + "=" * 60)
print("데모 데이터 생성 완료!")
print("=" * 60)
print(f"""
회사:        한국철강(주) (사업자번호: 123-45-67890)
사업장:      안산 제1공장, 인천 제2공장

로그인 계정:
  Admin          admin@hankook-steel.kr / admin123
  현장담당자(안산) park.jm@hankook-steel.kr / field123
  현장담당자(인천) choi.sh@hankook-steel.kr / field123
  작업자          kim.worker@hankook-steel.kr / worker123

데이터 현황:
  사고/아차사고    {len(incidents)}건 (6개월치)
  AI 분석         {len(ai_results)}건 (10건 x 3유형)
  익명 제보        {len(anon_reports)}건
  TBM 세션        {len(tbm_sessions)}회
  위험성평가       {len(risk_assessments)}건
  안전수칙 가이드  {len(guides)}건 + 번역 {len(translations)}건
  교육 이수        {len(training_records)}건
  포인트           {len(points)}건
  퀴즈             {len(quizzes)}건 (응답 {len(responses)}건)
  위험도 점수      {len(risk_scores)}건
  알림             {len(notifications)}건
""")

db.close()
