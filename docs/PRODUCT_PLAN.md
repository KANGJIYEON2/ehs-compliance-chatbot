# EHS 리스크 관리 SaaS 기획안

> **산안법 챗봇 → 기업형 EHS 리스크 관리 SaaS 전환 기획**
> **듀얼 트랙: 관리자 시스템 + 현장 작업자 도구**

---

## 0. 제품 비전

```
┌─────────────────────────────────────────────────────┐
│              EHS 리스크 관리 플랫폼                    │
│                                                     │
│  ┌──────────────────┐   ┌────────────────────────┐  │
│  │  관리자 트랙 (Web) │   │  작업자 트랙 (Mobile)   │  │
│  │                  │   │                        │  │
│  │ - 사고 관리       │◄──│ - 음성 현장 보고        │  │
│  │ - 대시보드        │◄──│ - 익명 위험 제보        │  │
│  │ - AI 분석/예방    │   │ - 다국어 안전 안내      │  │
│  │ - 컴플라이언스    │   │ - 안전 게이미피케이션   │  │
│  │ - 리포트 생성     │   │ - 위험 예측 알림        │  │
│  │ - 법령 근거 엔진  │   │                        │  │
│  └────────┬─────────┘   └───────────┬────────────┘  │
│           │                         │                │
│           └────────┐   ┌────────────┘                │
│                    ▼   ▼                             │
│              ┌──────────────┐                        │
│              │  공유 데이터  │                        │
│              │  PostgreSQL  │                        │
│              │  + FAISS RAG │                        │
│              └──────────────┘                        │
└─────────────────────────────────────────────────────┘
```

**핵심 컨셉:** 관리자가 보는 대시보드와 작업자가 쓰는 현장 도구가 **같은 DB를 먹고**, 서로 데이터를 순환시키는 구조.

- 작업자가 음성으로 보고 → 관리자 대시보드에 실시간 반영
- 익명 제보 → 잠재 위험 히트맵에 합산
- 관리자가 조치 완료 → 작업자 TBM 안건에 반영
- 사고 데이터 축적 → 예측 스코어링 정확도 상승

---

## 1. 현재 상태 (AS-IS)

| 항목 | 현재 |
|------|------|
| 제품 형태 | 법령 RAG 챗봇 (단일 사용자) |
| 인증 | 없음 |
| DB | FAISS 벡터 DB만 (사고 데이터 저장 불가) |
| 사용자 구조 | 없음 (익명) |
| 데이터 | 법령 텍스트 + 규칙 별표 (정적) |
| 가치 제안 | "산안법 조항 검색이 편하다" |

## 2. 목표 상태 (TO-BE)

| 항목 | 목표 |
|------|------|
| 제품 형태 | **기업형 EHS 리스크 관리 플랫폼 (듀얼 트랙)** |
| 인증 | 기업 회원가입 + 역할 기반 권한 (관리자 / 현장담당자 / 작업자) |
| DB | PostgreSQL (사고/제보/사용자/게임) + FAISS (법령 RAG) |
| 사용자 구조 | 기업 → 사업장 → 부서/공정 |
| 데이터 | 법령 + **실시간 사고/제보 데이터** + 조치 이력 + 행동 포인트 |
| 가치 제안 | "관리자는 리스크를 분석하고, 작업자는 현장에서 안전을 실천한다" |

---

## 3. 핵심 전환 포인트

```
[현재] 법령 챗봇 (질문 → 법조문 검색 → 답변)
                    ↓
[전환] 듀얼 트랙 EHS 플랫폼

  관리자 트랙 (데스크톱):
       ├── 사고/아차사고 등록 & 관리
       ├── 반복 사고 분석 대시보드
       ├── AI 예방 조치 추천 + 피드백 루프
       ├── 중대재해처벌법 컴플라이언스 체커
       ├── 월간 안전 리포트 자동 생성
       └── 법령 RAG = "근거 엔진" (보조 기능)

  작업자 트랙 (모바일 PWA):
       ├── 음성 기반 현장 보고 (Whisper API)
       ├── 익명 위험 제보 채널
       ├── 다국어 안전 안내 (QR 스캔)
       ├── 안전 행동 게이미피케이션
       └── 위험 예측 알림 수신
```

**데이터 순환 구조:**
```
작업자가 제보/보고  ──→  관리자 대시보드에 반영
        ↑                        │
        │                        ▼
작업자에게 알림 전달  ←──  관리자가 조치/분석
```

---

## 4. MVP 기능 명세 (1차)

### 4.1 회사/사업장 계정 구조

```
기업 (Company)
  ├── 사업장 (Site) - 여러 개 가능
  │     ├── 부서 (Department)
  │     ├── 공정 (Process)
  │     ├── 장비 (Equipment)
  │     └── 작업구역 (WorkZone)
  └── 사용자 (User)
        ├── 관리자 (Admin) - 전체 열람, 설정 관리
        └── 현장담당자 (FieldManager) - 사고 등록, 본인 사업장만
```

**구현 항목:**
- [ ] 기업 회원가입 (이메일 + 비밀번호)
- [ ] JWT 기반 인증 (access + refresh token)
- [ ] 사업장 CRUD
- [ ] 관리자 / 현장담당자 권한 분리
- [ ] 부서, 공정, 장비, 작업구역 마스터 데이터 관리

### 4.2 사고/아차사고 등록

**입력 항목:**
| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| 사고 유형 | Enum | O | 끼임, 추락, 충돌, 감전, 화재, 질식, 낙하물, 기타 |
| 심각도 | Enum | O | 사망, 중상, 경상, 아차사고 |
| 발생 일시 | DateTime | O | |
| 발생 위치 | FK(WorkZone) | O | 사업장 내 작업구역 |
| 관련 공정 | FK(Process) | △ | |
| 관련 장비 | FK(Equipment) | △ | |
| 원인 추정 | Text | O | 자유 텍스트 |
| 조치 내용 | Text | △ | |
| 사진/파일 | File[] | △ | 최대 5개 |
| 상태 | Enum | O | 접수 → 조치중 → 조치완료 → 재발관리 |
| 등록자 | FK(User) | 자동 | |

**상태 흐름:**
```
접수 → 조치중 → 조치완료 → (재발 시) 재발관리
  ↑                              ↓
  └────── 같은 유형 재발 감지 ──────┘
```

### 4.3 반복 사고 분석 대시보드

**핵심 화면:** 사고 유형별 통계 + 트렌드 + AI 인사이트

```
┌─────────────────────────────────────────────┐
│  📊 최근 3개월 사고 현황                      │
│                                             │
│  [끼임: 12건] [추락: 5건] [감전: 3건]         │
│                                             │
│  📈 월별 추이 차트 (Bar/Line)                │
│                                             │
│  🔴 주요 발견사항 (AI 분석)                   │
│  ┌─────────────────────────────────────────┐ │
│  │ 끼임사고 12건 중 8건이 프레스 공정 발생     │ │
│  │ 주요 원인: 방호덮개 미설치(5건),           │ │
│  │          접근통제 미흡(3건)               │ │
│  │                                         │ │
│  │ 💡 예방 조치 추천:                       │ │
│  │ ✅ 방호장치 일제 점검                     │ │
│  │ ✅ 비상정지 버튼 작동 확인                 │ │
│  │ ✅ 작업 전 TBM 강화                      │ │
│  │                                         │ │
│  │ 📋 관련 법령 근거:                       │ │
│  │ ▸ 산업안전보건기준에 관한 규칙 별표 12     │ │
│  │ ▸ 산업안전보건법 제38조 (안전조치)        │ │
│  └─────────────────────────────────────────┘ │
└─────────────────────────────────────────────┘
```

**구현 항목:**
- [ ] 사고 유형별 집계 API
- [ ] 기간별 트렌드 차트 (월/주)
- [ ] 위치별, 공정별, 장비별 필터링
- [ ] AI 패턴 분석 (GPT-4o-mini로 사고 데이터 요약)
- [ ] 관련 법령 자동 매칭 (기존 RAG 연동)

### 4.4 AI 예방 조치 추천 + 피드백 루프

```
사고 등록
  ↓
AI 예방 체크리스트 자동 생성
  ↓
관리자가 실제 조치 입력 (체크리스트 기반)
  ↓
조치 후 재발 여부 추적
  ↓
같은 유형 재발 시 → "조치 효과 낮음" 표시
  ↓
AI가 보완 조치 재추천
```

**핵심 로직:**
- 사고 등록 시 → GPT에 사고 유형 + 위치 + 원인 전달 → 예방 체크리스트 생성
- 체크리스트 항목마다 조치 완료/미완료 추적
- 조치 완료 후 동일 유형 재발 → 조치 효과 평가 (효과적/미흡/무효)
- 무효 판정 시 AI가 보완 조치 재추천

### 4.5 법령 RAG 재배치

**기존:** 메인 기능 (챗봇)
**변경:** 각 사고 유형 옆에 **근거 엔진**으로 배치

```
사고 상세 페이지
  ├── 사고 정보
  ├── AI 분석 결과
  ├── 예방 체크리스트
  ├── [관련 법령 근거 보기] ← 토글
  │     ├── 법조문 요약
  │     ├── 별표/원문 근거
  │     └── RAG 검색 결과
  └── 조치 이력
```

### 4.6 월간 안전 리포트 생성

**자동 생성 내용:**
- 이번 달 사고/아차사고 건수 및 유형 분포
- 전월 대비 증감
- 반복 사고 패턴 분석
- 미조치/미완료 항목 목록
- AI 추천 중점 관리 사항
- 관련 법령 근거 요약

**출력:** PDF 다운로드 or 웹 뷰

---

## 5. 작업자 트랙 기능 명세

### 5.1 음성 기반 현장 보고

현장 작업자는 장갑, 헬멧, 기름 묻은 손 — **폼 입력이 현실적으로 불가능.** 음성이면 3초에 끝남.

```
작업자: (음성) "3번 프레스 방호덮개 고정볼트 빠져있어요"
    ↓
OpenAI Whisper API → 텍스트 변환
    ↓
GPT가 자동 파싱:
  - 위치: 프레스 공정, 3번 장비
  - 유형: 장비 결함
  - 위험도: 높음 (끼임 위험)
    ↓
사고/위험 보고 자동 생성 (작업자는 확인만 누름)
    ↓
관리자 대시보드에 즉시 반영
```

**구현 항목:**
- [ ] 모바일 PWA 음성 녹음 UI (MediaRecorder API)
- [ ] Whisper API 연동 (be/services/speech_service.py)
- [ ] GPT 구조화 파싱 (위치, 유형, 위험도 자동 추출)
- [ ] 파싱 결과 확인/수정 UI → 사고 테이블에 저장
- [ ] 관리자에게 실시간 알림

**기술 포인트:**
- Whisper API: 한국어 인식률 우수, 현장 소음 환경에서도 동작
- 구조화 파싱 프롬프트: 사업장의 공정/장비 목록을 컨텍스트로 전달하면 매칭 정확도 상승
- 녹음 → 전송 → 파싱 → 확인까지 10초 이내 목표

### 5.2 익명 위험 제보 채널

현장에서 위험한 걸 알아도 **"말하면 불이익"** 때문에 안 말함. 이게 대형사고로 이어짐.
중대재해처벌법 제4조 **"종사자 의견 청취 의무"** — 법적 근거도 있음.

```
익명 제보 접수 (텍스트 / 사진 / 음성)
    ↓
AI가 위험 등급 자동 분류
  - 긴급 (즉시 조치 필요)
  - 주의 (1주 내 조치)
  - 개선 (장기 과제)
    ↓
긴급 → 관리자에게 즉시 알림
    ↓
조치 결과가 익명 제보자에게 피드백
  (제보자 신원 노출 없이 "조치 완료" 알림)
```

**핵심 설계 — 익명성 보장:**
```
제보 저장 시:
  ✅ 제보 내용, 사진, 위험 등급
  ✅ 익명 토큰 (피드백 수신용, 1회용 UUID)
  ❌ 사용자 ID, IP, 디바이스 정보 일절 저장 안 함
```

**구현 항목:**
- [ ] 익명 제보 API (POST /api/reports/anonymous)
- [ ] 익명 토큰 발급 → 제보자가 토큰으로 조치 결과 확인
- [ ] AI 위험 등급 자동 분류 (GPT)
- [ ] 긴급 제보 → 관리자 알림 (이메일 / 웹 푸시)
- [ ] 관리자용 제보 관리 화면 (조치 입력, 상태 변경)
- [ ] 제보 데이터 → 잠재 위험 히트맵에 합산

**DB 설계:**
```sql
CREATE TABLE anonymous_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    site_id UUID REFERENCES sites(id) NOT NULL,
    anonymous_token UUID NOT NULL UNIQUE,  -- 피드백 조회용 (사용자 식별 불가)

    content TEXT NOT NULL,
    risk_level VARCHAR(20) NOT NULL,      -- critical, warning, improvement
    ai_category VARCHAR(30),              -- AI가 분류한 위험 유형
    location_hint TEXT,                   -- 대략적 위치 (제보자가 자유 입력)

    status VARCHAR(20) DEFAULT 'received', -- received → reviewing → resolved
    admin_response TEXT,                   -- 조치 결과 (제보자에게 피드백)

    created_at TIMESTAMP DEFAULT NOW(),
    resolved_at TIMESTAMP
    -- 주의: user_id, ip_address 등 신원 관련 컬럼 없음
);

CREATE TABLE report_attachments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    report_id UUID REFERENCES anonymous_reports(id),
    file_path VARCHAR(500) NOT NULL,
    uploaded_at TIMESTAMP DEFAULT NOW()
);
```

### 5.3 다국어 안전 안내 (QR 스캔)

제조/건설 현장의 외국인 근로자 — **한국어 안전교육을 못 알아듣는 게 사고 원인 상위권.**

```
장비/구역에 QR코드 부착
    ↓
작업자가 모바일로 QR 스캔
    ↓
브라우저 언어 감지 or 언어 선택
    ↓
해당 장비/구역의 안전수칙이 본인 언어로 표시
  (한국어 / 베트남어 / 캄보디아어 / 네팔어 / 영어)
    ↓
TTS 음성 안내 (선택)
    ↓
"이해했습니다" 확인 → 교육 이수 기록 자동 저장
```

**구현 항목:**
- [ ] 장비/구역별 안전수칙 관리 (관리자가 한국어로 입력)
- [ ] GPT-4o 다국어 번역 API (/api/safety-guide/:equipmentId?lang=vi)
- [ ] QR코드 생성 (장비/구역 ID 인코딩)
- [ ] 모바일 웹 안전수칙 뷰어 (번역 + TTS)
- [ ] 교육 이수 기록 저장 (어떤 장비, 어떤 언어, 언제)
- [ ] 관리자용: 교육 이수 현황 대시보드

**지원 언어 (한국 제조/건설 현장 기준):**
| 순위 | 언어 | 비율 |
|------|------|------|
| 1 | 베트남어 | ~35% |
| 2 | 캄보디아어 | ~15% |
| 3 | 네팔어 | ~12% |
| 4 | 미얀마어 | ~10% |
| 5 | 영어 | 기타 |

**DB 설계:**
```sql
CREATE TABLE safety_guides (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    site_id UUID REFERENCES sites(id),
    target_type VARCHAR(20) NOT NULL,     -- 'equipment' or 'work_zone'
    target_id UUID NOT NULL,              -- equipment.id or work_zone.id
    content_ko TEXT NOT NULL,             -- 원문 (한국어)
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE safety_guide_translations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    guide_id UUID REFERENCES safety_guides(id),
    language VARCHAR(10) NOT NULL,        -- vi, km, ne, my, en
    content TEXT NOT NULL,                -- 번역 결과 (캐싱)
    translated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE training_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    guide_id UUID REFERENCES safety_guides(id),
    language VARCHAR(10) NOT NULL,
    acknowledged_at TIMESTAMP DEFAULT NOW()
    -- 비로그인 사용자도 기록 가능 (user_id 선택적)
);
```

### 5.4 안전 행동 게이미피케이션

안전 교육/점검을 **의무가 아니라 게임으로** 만들면 참여율이 완전히 달라짐.

```
📊 이번 주 안전 랭킹
━━━━━━━━━━━━━━━━━━━━
🥇 프레스 1팀    850점  (+120)
🥈 도장팀       720점  (+80)
🥉 조립 2팀     680점  (+45)

점수 획득 방법:
  +50  위험 제보 등록
  +30  TBM 참석 완료
  +20  안전 퀴즈 정답
  +10  안전수칙 QR 확인
  +100 무사고 1주 달성
  -200 안전수칙 위반 적발
```

**구현 항목:**
- [ ] 포인트 시스템 (행동별 점수 적립/차감)
- [ ] 팀(부서) 단위 랭킹 보드
- [ ] AI 안전 퀴즈 (GPT가 최근 사고 + 법령 기반으로 매일 자동 생성)
- [ ] 주간/월간 랭킹 + 보상 관리
- [ ] 개인 안전 활동 히스토리

**데이터 연동:**
- 제보 등록 → +50점 자동 적립
- QR 안전수칙 확인 → +10점 자동 적립
- 사고 발생 → 해당 팀 -200점
- TBM 참석 → +30점 (관리자가 확인)

**DB 설계:**
```sql
CREATE TABLE safety_points (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    site_id UUID REFERENCES sites(id),
    points INTEGER NOT NULL,
    reason VARCHAR(50) NOT NULL,          -- report, tbm, quiz, qr_check, no_accident, violation
    reference_id UUID,                    -- 관련 제보/사고/퀴즈 ID
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE safety_quizzes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    site_id UUID REFERENCES sites(id),
    question TEXT NOT NULL,
    options JSONB NOT NULL,               -- ["선택지1", "선택지2", "선택지3", "선택지4"]
    correct_index INTEGER NOT NULL,
    explanation TEXT,                     -- 정답 해설
    source_incident_id UUID,             -- 출처 사고 (있으면)
    generated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE quiz_responses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    quiz_id UUID REFERENCES safety_quizzes(id),
    user_id UUID REFERENCES users(id),
    selected_index INTEGER NOT NULL,
    is_correct BOOLEAN NOT NULL,
    answered_at TIMESTAMP DEFAULT NOW()
);
```

### 5.5 사고 예측 스코어링

사고 데이터가 쌓이면 **"다음 사고가 어디서 터질 확률이 높은지"** 예측.

```
🔮 이번 주 위험 예측
━━━━━━━━━━━━━━━━━━━
프레스 공정    위험도 92%  🔴
  근거: 끼임사고 3건/월, 방호장치 미점검 2주째,
       신규 작업자 2명 투입, 잔업 증가

컨베이어 라인  위험도 65%  🟡
  근거: 추락사고 1건/월, 안전난간 보수 미완료

도장 공정     위험도 25%  🟢
```

**위험도 산정 공식 (가중 점수 모델):**
```
위험도 = (사고빈도 × 30) + (미조치 × 25) + (신규작업자 × 15)
       + (잔업시간 × 15) + (제보건수 × 10) + (계절요인 × 5)

각 요인 0~100 정규화 후 가중합산
```

**구현 항목:**
- [ ] 위험도 산정 API (공정/구역별)
- [ ] 입력 변수 수집 (사고 이력, 점검 현황, 작업자 정보, 제보 데이터)
- [ ] 주간 자동 산정 + 변동 추적
- [ ] 관리자 대시보드: 위험 예측 카드
- [ ] 작업자 앱: 본인 공정 위험도 알림
- [ ] GPT 분석: 위험도 높은 공정에 대한 상세 분석 + 추천

**DB 설계:**
```sql
CREATE TABLE risk_scores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    site_id UUID REFERENCES sites(id),
    target_type VARCHAR(20) NOT NULL,     -- 'process' or 'work_zone'
    target_id UUID NOT NULL,
    score INTEGER NOT NULL,               -- 0~100
    factors JSONB NOT NULL,               -- 각 요인별 점수 상세
    calculated_at TIMESTAMP DEFAULT NOW()
);
```

---

## 6. 기술 아키텍처 (TO-BE)

### 6.1 시스템 구성도

```
┌──────────────────┐     ┌──────────────────────┐
│  관리자 Web SPA   │     │  작업자 Mobile PWA    │
│  (React Desktop)  │     │  (React Responsive)   │
└────────┬─────────┘     └──────────┬───────────┘
         │                          │
         └──────────┬───────────────┘
                    ↓ REST API (JWT)
         ┌──────────────────────────┐
         │   FastAPI Backend         │
         ├──────────────────────────┤
         │ Auth Module               │ JWT + bcrypt + 3-role
         │ Incident Module           │ 사고 CRUD + 상태관리
         │ Anonymous Report Module   │ 익명 제보 + 토큰 피드백
         │ Speech Module             │ Whisper → 텍스트 → 구조화
         │ Safety Guide Module       │ 다국어 번역 + QR + TTS
         │ Gamification Module       │ 포인트 + 랭킹 + 퀴즈
         │ Risk Score Module         │ 예측 스코어링
         │ Analytics Module          │ 집계 + AI 분석
         │ RAG Module                │ FAISS + OpenAI (근거 엔진)
         │ Report Gen Module         │ 월간 리포트 + PDF
         └──────────┬───────────────┘
                    ↓
         ┌──────────────────────────┐
         │ PostgreSQL                │ 사고/제보/사용자/포인트
         │ FAISS                     │ 법령 벡터 DB (기존)
         │ OpenAI API                │ Whisper + Embed + Chat
         └──────────────────────────┘
```

### 6.2 DB 스키마 설계 (PostgreSQL)

```sql
-- 기업
CREATE TABLE companies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(200) NOT NULL,
    business_number VARCHAR(20) UNIQUE,  -- 사업자등록번호
    created_at TIMESTAMP DEFAULT NOW()
);

-- 사업장
CREATE TABLE sites (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(id),
    name VARCHAR(200) NOT NULL,
    address TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 사용자
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(id),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(100) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('admin', 'field_manager', 'worker')),
    site_id UUID REFERENCES sites(id),  -- 현장담당자는 특정 사업장 배정
    created_at TIMESTAMP DEFAULT NOW()
);

-- 부서
CREATE TABLE departments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    site_id UUID REFERENCES sites(id),
    name VARCHAR(200) NOT NULL
);

-- 공정
CREATE TABLE processes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    site_id UUID REFERENCES sites(id),
    name VARCHAR(200) NOT NULL
);

-- 장비
CREATE TABLE equipment (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    site_id UUID REFERENCES sites(id),
    name VARCHAR(200) NOT NULL,
    process_id UUID REFERENCES processes(id)
);

-- 작업구역
CREATE TABLE work_zones (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    site_id UUID REFERENCES sites(id),
    name VARCHAR(200) NOT NULL
);

-- 사고/아차사고
CREATE TABLE incidents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    site_id UUID REFERENCES sites(id) NOT NULL,
    reporter_id UUID REFERENCES users(id) NOT NULL,

    -- 사고 정보
    incident_type VARCHAR(30) NOT NULL,  -- 끼임, 추락, 충돌, 감전, 화재, 질식, 낙하물, 기타
    severity VARCHAR(20) NOT NULL,       -- death, serious, minor, near_miss
    occurred_at TIMESTAMP NOT NULL,

    -- 위치/관련 정보
    work_zone_id UUID REFERENCES work_zones(id),
    process_id UUID REFERENCES processes(id),
    equipment_id UUID REFERENCES equipment(id),
    department_id UUID REFERENCES departments(id),

    -- 상세
    description TEXT NOT NULL,           -- 사고 설명
    cause_estimate TEXT,                 -- 원인 추정
    action_taken TEXT,                   -- 조치 내용

    -- 상태
    status VARCHAR(20) NOT NULL DEFAULT 'reported',
    -- reported → investigating → resolved → monitoring

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 사고 첨부파일
CREATE TABLE incident_attachments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    incident_id UUID REFERENCES incidents(id),
    file_path VARCHAR(500) NOT NULL,
    file_type VARCHAR(50),
    uploaded_at TIMESTAMP DEFAULT NOW()
);

-- AI 예방 체크리스트
CREATE TABLE prevention_checklists (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    incident_id UUID REFERENCES incidents(id),
    generated_at TIMESTAMP DEFAULT NOW(),
    ai_model VARCHAR(50) DEFAULT 'gpt-4o-mini'
);

-- 체크리스트 항목
CREATE TABLE checklist_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    checklist_id UUID REFERENCES prevention_checklists(id),
    content TEXT NOT NULL,               -- 조치 항목 내용
    is_completed BOOLEAN DEFAULT FALSE,
    completed_at TIMESTAMP,
    completed_by UUID REFERENCES users(id),
    effectiveness VARCHAR(20)            -- effective, insufficient, ineffective
);

-- 법령 근거 연결
CREATE TABLE incident_legal_refs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    incident_id UUID REFERENCES incidents(id),
    law_name VARCHAR(200),
    article_id VARCHAR(50),
    content TEXT,
    relevance_score FLOAT
);
```

### 6.3 주요 API 설계

```
# ──────────────── 공통 ────────────────
# Auth
POST   /api/auth/register              # 기업 회원가입
POST   /api/auth/login                  # 로그인 → JWT
POST   /api/auth/refresh                # 토큰 갱신
GET    /api/auth/me                     # 내 정보

# 조직 관리 (admin)
GET    /api/sites                       # 사업장 목록
POST   /api/sites                       # 사업장 생성
CRUD   /api/sites/:id/departments       # 부서
CRUD   /api/sites/:id/processes         # 공정
CRUD   /api/sites/:id/equipment         # 장비
CRUD   /api/sites/:id/work-zones        # 작업구역

# ──────────────── 관리자 트랙 ────────────────
# 사고 관리
GET    /api/incidents                   # 사고 목록 (필터/페이징)
POST   /api/incidents                   # 사고 등록
GET    /api/incidents/:id               # 사고 상세
PATCH  /api/incidents/:id               # 사고 수정/상태 변경
POST   /api/incidents/:id/files         # 파일 첨부

# AI 분석
POST   /api/incidents/:id/analyze       # AI 분석 트리거
GET    /api/incidents/:id/checklist     # 예방 체크리스트 조회
PATCH  /api/incidents/:id/checklist/:itemId

# 대시보드
GET    /api/analytics/summary           # 요약 통계
GET    /api/analytics/trend             # 기간별 트렌드
GET    /api/analytics/by-type           # 유형별 분석
GET    /api/analytics/recurring         # 반복 사고 분석
GET    /api/analytics/risk-scores       # 위험 예측 스코어

# 법령 RAG (근거 엔진)
POST   /api/rag/ask                     # 법령 질의 (기존 /ask)
GET    /api/rag/health                  # RAG DB 상태

# 리포트
POST   /api/reports/monthly             # 월간 리포트 생성
GET    /api/reports/:id/download        # 리포트 다운로드

# 익명 제보 관리 (admin)
GET    /api/anonymous-reports           # 제보 목록
PATCH  /api/anonymous-reports/:id       # 조치 입력/상태 변경

# ──────────────── 작업자 트랙 ────────────────
# 음성 보고
POST   /api/voice/transcribe            # 음성 → 텍스트 (Whisper)
POST   /api/voice/parse                 # 텍스트 → 구조화 (GPT)
POST   /api/voice/submit                # 구조화 결과 → 사고 등록

# 익명 제보
POST   /api/anonymous-reports           # 익명 제보 등록 (인증 불필요)
GET    /api/anonymous-reports/check/:token  # 토큰으로 조치 결과 확인

# 다국어 안전 안내
GET    /api/safety-guide/:targetId      # 장비/구역 안전수칙 (lang 파라미터)
POST   /api/safety-guide/:targetId/ack  # 교육 이수 확인
GET    /api/qr/:targetId                # QR코드 이미지 생성

# 게이미피케이션
GET    /api/gamification/ranking        # 팀 랭킹
GET    /api/gamification/my-points      # 내 포인트 히스토리
GET    /api/gamification/quiz/today     # 오늘의 퀴즈
POST   /api/gamification/quiz/:id/answer # 퀴즈 답변 제출

# 위험 알림
GET    /api/risk/my-zone                # 내 공정/구역 위험도
```

---

## 7. 개발 로드맵

### Phase 1: 기반 구축 ✅
> 모노레포 셋업 + DB + Auth + 조직 구조

- [x] 모노레포 구조 전환 (packages/api, apps/admin, apps/worker)
- [x] SQLAlchemy + Alembic 마이그레이션 (SQLite 개발, PostgreSQL 전환 가능)
- [x] 기업/사업장/사용자 모델 + CRUD
- [x] JWT 인증 (회원가입, 로그인, 토큰 갱신)
- [x] 권한 미들웨어 (admin / field_manager / worker)
- [x] 마스터 데이터 CRUD (부서, 공정, 장비, 작업구역)
- [x] admin 앱: 로그인/회원가입 UI + React Router + Zustand

### Phase 2: 관리자 트랙 - 사고 관리 ✅
> 사고 등록 + 목록 + 상세

- [x] 사고/아차사고 CRUD API (9개 유형, 4단계 심각도)
- [x] 파일 업로드 (로컬, 10MB, image/pdf)
- [x] 사고 상태 관리 (접수 → 조치중 → 조치완료 → 재발관리)
- [x] admin 앱: 사고 등록 폼, 사고 목록 (유형/상태 필터, 페이징), 사고 상세

### Phase 3: 관리자 트랙 - AI 분석 ✅
> AI Agent 아키텍처 + 예방 체크리스트 + 법령 근거

- [x] AI Agent 아키텍처 (BaseAgent + 4개 전문 에이전트)
- [x] IncidentAgent: 원인 분석 + 예방 체크리스트 + 재발 방지
- [x] LawAgent: 관련 법조문 + 사업주 의무 + 처벌 요약
- [x] AI 분석 결과 DB 캐싱 (24시간 TTL)
- [x] 사고 상세에 3개 AI 버튼 (원인분석/체크리스트/법령근거)
- [x] 기존 챗봇 기능을 `/api/rag/ask`로 이전

### Phase 4: 관리자 트랙 - 대시보드 + 리포트 ✅
> 통계 + 차트 + 뉴스 + 리포트

- [x] 사고 유형별/심각도별/상태별/월별 집계 API
- [x] admin 앱: 대시보드 (Recharts Bar + Pie 차트)
- [x] 산업안전 뉴스 RSS + NewsAgent AI 분석 (30분 캐싱)
- [x] 월간 안전 리포트 PDF 자동 생성 (AI 요약 포함)
- [x] 대시보드에 통계 카드 + 뉴스 피드 + PDF 다운로드 버튼

### Phase 5: 작업자 트랙 - 핵심 기능 ✅
> 음성 보고 + 익명 제보 + 다국어 안내

- [x] VoiceAgent: Whisper STT → GPT 구조화 파싱
- [x] 음성 보고 UI: 녹음 → 전사 → 파싱 → 리뷰 → 사고 자동 등록
- [x] 익명 제보: 인증 없이 제보 → AI 위험등급 분류 → 토큰 발급
- [x] 관리자 제보 관리 페이지 (조치 입력 → 제보자에게 피드백)
- [x] 다국어 안전 안내: 한국어 원문 → GPT 번역 (vi/en/km/ne/my)
- [x] QR코드 생성 + 공개 뷰 (인증 불필요) + 교육 이수 기록
- [ ] worker PWA 앱 셋업 (현재 admin 앱에 통합)

### Phase 6: 작업자 트랙 - 게이미피케이션 + 예측 ✅
> 포인트 시스템 + 위험 예측

- [x] 포인트 적립/차감 로직 + 팀 랭킹 API
- [x] AI 안전 퀴즈 자동 생성 (매일 1문제) + 답변 시 포인트
- [x] 위험도 스코어링 엔진 (가중 점수: 사고빈도×30 + 미조치×25)
- [x] 위험도 재계산 API
- [ ] worker 앱: 랭킹 보드, 퀴즈 UI, 내 공정 위험도 (프론트 미구현)
- [ ] admin 앱: 위험 예측 대시보드 카드 (프론트 미구현)

### Phase 7: 통합 + 폴리싱 (미착수)
> 두 트랙 연동 + 마무리

- [ ] worker PWA 앱 분리 (apps/worker/)
- [ ] 데이터 순환 검증 (작업자 제보 → 관리자 대시보드 → 작업자 알림)
- [ ] 프론트 추가 페이지: 퀴즈 UI, 랭킹 보드, 위험 예측 카드
- [ ] 전체 UI 폴리싱 + 에러 핸들링 + 로딩/빈 상태
- [ ] Docker Compose 프로덕션 설정
- [ ] 배포 (Cloudtype or Railway)

**실제 소요: Phase 1-6 백엔드 + 핵심 프론트 완료**
**남은 작업: Worker PWA 분리, 프론트 추가 페이지, UI 폴리싱, 프로덕션 배포**

---

## 8. 기술 스택 변경사항

| 영역 | 변경 전 | 변경 후 (구현 완료) |
|------|---------|---------------------|
| 프로젝트 구조 | 단일 be/ + fe/ | **모노레포** (packages/api, apps/admin, apps/worker) |
| DB | FAISS only | **+ SQLAlchemy 2.0 + Alembic** (SQLite dev, PostgreSQL ready) |
| Auth | 없음 | **+ JWT** (python-jose + bcrypt) + 3-role |
| AI | OpenAI 직접 호출 | **AI Agent 아키텍처** (BaseAgent + 4개 전문 에이전트) |
| 프론트 라우팅 | 없음 (단일 페이지) | **+ React Router v7** (10 routes) |
| 상태관리 | useState only | **+ Zustand** (persist middleware) |
| 차트 | 없음 | **+ Recharts** (Bar + Pie) |
| 음성 | 없음 | **+ OpenAI Whisper API** (VoiceAgent) |
| QR | 없음 | **+ qrcode** (Python) |
| 파일업로드 | 없음 | **+ python-multipart** (10MB, image/pdf) |
| PDF 생성 | 없음 | **+ reportlab** (한글 폰트 자동 감지) |
| 뉴스 | 없음 | **+ Google News RSS** + NewsAgent |

---

## 9. 이력서 표현 예시

### 한 줄 요약
> 관리자-작업자 듀얼 트랙 구조로, 사고 데이터 분석/예방 조치/법령 근거/음성 보고/다국어 안전 안내를 통합한 기업형 EHS 리스크 관리 플랫폼 개발

### 프로젝트 상세
```
EHS 리스크 관리 SaaS 플랫폼 (듀얼 트랙)

[AI Agent 아키텍처]
- 4개 독립 AI Agent 설계 (뉴스분석/사고분석/법령검색/음성처리)
- 분석 결과 DB 캐싱 (24시간 TTL)으로 API 비용 최적화

[관리자 트랙]
- 기업/사업장/역할 기반 다중 테넌트 구조 (JWT 3-role 인증)
- 사고/아차사고 CRUD + 상태 워크플로우 (접수→조치중→완료→재발관리)
- AI 원인 분석 + 예방 체크리스트 + 관련 법령 근거 자동 생성
- 대시보드: 사고 통계 차트 (Recharts) + 산업안전 뉴스 AI 분석
- 월간 안전 리포트 PDF 자동 생성 (AI 요약 포함)
- 가중 점수 모델 기반 사고 예측 스코어링 엔진

[작업자 트랙]
- Whisper API 음성 현장 보고 → GPT 구조화 파싱 → 사고 자동 등록
- 신원 비저장 설계 익명 위험 제보 (AI 위험등급 분류, 토큰 기반 피드백)
- GPT 다국어 번역 + QR 스캔 기반 외국인 근로자 안전 안내 (5개 언어)
- 안전 행동 게이미피케이션 (포인트/랭킹/AI 퀴즈 자동 생성)

Tech: FastAPI, React, SQLAlchemy, FAISS, OpenAI API (GPT-4o-mini + Whisper),
      Recharts, ReportLab, Docker
```

---

## 10. 차별화 포인트

| vs 경쟁 | 우리의 강점 |
|---------|------------|
| 엑셀 관리 | 실시간 데이터 + AI 분석 + 예측 |
| 단순 EHS SW | **법령 RAG 근거 엔진** 내장 |
| 일반 챗봇 | 사고 데이터 기반 **예방 조치 자동화** |
| 외산 EHS SaaS | **한국 산안법** 특화 + 다국어 외국인 근로자 지원 |
| 관리자 전용 시스템 | **듀얼 트랙** — 작업자도 직접 참여 (음성 보고, 제보, 퀴즈) |
| 강제적 안전 교육 | **게이미피케이션**으로 자발적 안전 행동 유도 |

---

## 11. 고민 포인트 & 의사결정 가이드

### 고민 1: 풀스택 혼자 다 할 수 있나?
- 관리자 트랙 MVP (Phase 1-4) = 7.5주, 이것만으로 포트폴리오 가능
- 작업자 트랙 (Phase 5-7) = 5주 추가, 이거까지 하면 차별화 극대화
- **추천:** Phase 1-4 먼저 완성 → 배포 → Phase 5-7 추가

### 고민 2: PostgreSQL vs SQLite?
- **SQLite:** 배포 간편, 별도 서버 불필요, 1인 개발에 충분
- **PostgreSQL:** 프로덕션 급, 동시 접속 처리, JSON 연산, 이력서에 더 강함
- **추천:** 개발은 SQLite로 시작, SQLAlchemy 쓰면 나중에 PostgreSQL로 바로 전환 가능

### 고민 3: 프론트엔드 프레임워크 추가?
- 현재 순수 React + Vite로 충분
- Next.js 전환은 불필요한 복잡도 (SSR 필요 없음)
- **추천:** 현재 스택 유지, React Router + Zustand만 추가

### 고민 4: 배포 전략?
- 현재 Cloudtype 사용 중
- PostgreSQL 추가되면 Supabase (무료 티어) or Railway
- **추천:** Supabase PostgreSQL (무료) + Cloudtype (BE/FE)

### 고민 5: 기존 RAG 챗봇은 어떻게 하나?
- **버리지 말 것.** 가장 큰 자산
- `/api/rag/ask`로 API 경로만 이전
- 사고 상세 페이지에서 "관련 법령 근거 보기" 토글로 연동
- 대시보드 AI 분석에서 법령 근거 자동 첨부
- **결론:** 메인 → 보조로 역할만 바뀜, 코드는 거의 그대로

### 고민 6: 법령 데이터 관리 (API 분리)
- 법령은 자주 개정됨 → 벡터 DB에 하드코딩하면 안 됨
- **방안 A:** 국가법령정보센터 Open API 연동 → 변경 감지 → 자동 재임베딩
- **방안 B:** 법령 API를 별도 마이크로서비스로 분리, 메인 API에서 호출
- **추천:** 우선 law_api/client.py에서 국가법령정보센터 API 호출 + 캐싱,
  변경 감지 시 벡터 DB 재빌드 스크립트 트리거

### 고민 7: 모노레포 구조
- 관리자 앱 / 작업자 앱 / API가 독립 배포 가능해야 함
- **구조:** packages/api + apps/admin + apps/worker
- 프론트 두 앱은 같은 Zustand/fetch 유틸 공유 가능 → 공통 패키지 분리도 가능
- **추천:** 초반엔 단순 디렉토리 분리, npm workspaces는 필요할 때 도입

---

## 부록: 모노레포 파일 구조 (TO-BE)

```
ehs-compliance-chatbot/
│
├── packages/
│   └── api/                           # FastAPI 백엔드 (공유)
│       ├── main.py                    # App factory + 라우터 등록
│       ├── config.py                  # 설정 관리
│       ├── database.py                # SQLAlchemy 엔진/세션
│       ├── Dockerfile
│       ├── requirements.txt
│       │
│       ├── models/                    # SQLAlchemy 모델
│       │   ├── user.py
│       │   ├── company.py
│       │   ├── site.py
│       │   ├── incident.py
│       │   ├── checklist.py
│       │   ├── anonymous_report.py
│       │   ├── safety_guide.py
│       │   ├── gamification.py
│       │   └── risk_score.py
│       │
│       ├── schemas/                   # Pydantic 스키마
│       │   ├── auth.py
│       │   ├── incident.py
│       │   ├── report.py
│       │   ├── guide.py
│       │   ├── gamification.py
│       │   └── analytics.py
│       │
│       ├── routers/                   # API 라우터
│       │   ├── auth.py
│       │   ├── sites.py
│       │   ├── incidents.py           # 관리자 트랙
│       │   ├── analytics.py           # 관리자 트랙
│       │   ├── anonymous_reports.py   # 작업자 제보 + 관리자 조치
│       │   ├── voice.py               # 작업자 음성 보고
│       │   ├── safety_guide.py        # 작업자 다국어 안내
│       │   ├── gamification.py        # 작업자 포인트/퀴즈
│       │   ├── risk.py                # 예측 스코어
│       │   ├── rag.py                 # 법령 근거 엔진
│       │   └── reports.py             # 월간 리포트
│       │
│       ├── services/                  # 비즈니스 로직
│       │   ├── auth_service.py
│       │   ├── incident_service.py
│       │   ├── ai_service.py          # AI 분석 + 체크리스트
│       │   ├── speech_service.py      # Whisper + GPT 파싱
│       │   ├── translation_service.py # 다국어 번역
│       │   ├── gamification_service.py
│       │   ├── risk_service.py        # 예측 스코어링
│       │   ├── rag_service.py         # 기존 RAG 로직
│       │   └── report_service.py      # PDF 생성
│       │
│       ├── migrations/                # Alembic
│       │
│       ├── law_api/                   # 법령 API (분리)
│       │   ├── client.py              # 외부 법령 API 클라이언트
│       │   └── sync.py               # 법령 변경 감지 + 벡터 DB 갱신
│       │
│       ├── vector_db_law/             # 기존 유지
│       ├── vector_db_rule/            # 기존 유지
│       ├── extracted_rule/            # 기존 유지
│       └── scripts/                   # 기존 유지
│
├── apps/
│   ├── admin/                         # 관리자 웹 앱 (React + Vite)
│   │   ├── src/
│   │   │   ├── App.tsx
│   │   │   ├── router.tsx
│   │   │   ├── stores/               # Zustand
│   │   │   │   ├── authStore.ts
│   │   │   │   └── incidentStore.ts
│   │   │   ├── pages/
│   │   │   │   ├── LoginPage.tsx
│   │   │   │   ├── DashboardPage.tsx
│   │   │   │   ├── IncidentListPage.tsx
│   │   │   │   ├── IncidentDetailPage.tsx
│   │   │   │   ├── IncidentFormPage.tsx
│   │   │   │   ├── ReportsPage.tsx
│   │   │   │   ├── CompliancePage.tsx
│   │   │   │   ├── SettingsPage.tsx
│   │   │   │   └── RagChatPage.tsx    # 기존 챗봇 (보조)
│   │   │   ├── components/
│   │   │   │   ├── layout/
│   │   │   │   │   ├── Sidebar.tsx
│   │   │   │   │   └── Header.tsx
│   │   │   │   ├── incidents/
│   │   │   │   ├── dashboard/
│   │   │   │   ├── reports/           # 익명 제보 관리
│   │   │   │   └── chat/              # 기존 챗봇 컴포넌트
│   │   │   ├── hooks/
│   │   │   └── utils/
│   │   │       └── api.ts             # fetch 래퍼 (JWT)
│   │   ├── package.json
│   │   └── vite.config.ts
│   │
│   └── worker/                        # 작업자 모바일 PWA (React + Vite)
│       ├── src/
│       │   ├── App.tsx
│       │   ├── router.tsx
│       │   ├── stores/
│       │   │   └── workerStore.ts
│       │   ├── pages/
│       │   │   ├── HomePage.tsx        # 메인 (퀵 액션)
│       │   │   ├── VoiceReportPage.tsx # 음성 보고
│       │   │   ├── AnonymousPage.tsx   # 익명 제보
│       │   │   ├── SafetyGuidePage.tsx # QR 스캔 → 안전수칙
│       │   │   ├── RankingPage.tsx     # 팀 랭킹
│       │   │   ├── QuizPage.tsx        # 오늘의 퀴즈
│       │   │   └── MyPage.tsx          # 내 포인트/활동
│       │   ├── components/
│       │   │   ├── VoiceRecorder.tsx
│       │   │   ├── QRScanner.tsx
│       │   │   ├── QuizCard.tsx
│       │   │   └── RiskAlert.tsx
│       │   └── utils/
│       │       └── api.ts
│       ├── manifest.json              # PWA 매니페스트
│       ├── package.json
│       └── vite.config.ts
│
├── docker-compose.yml                 # API + PostgreSQL + admin + worker
├── .env
└── README.md
```
