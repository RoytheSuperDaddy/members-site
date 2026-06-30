# N잡크루 콘텐츠 자동 입력 에이전트 설계서

**버전**: v1.0 (Final)
**작성일**: 2026-05-16
**용도**: Claude Code 구현 시 참조 계획서
**대상 프로젝트**: N잡크루 멤버스 허브 (`sfmi.members-center.co.kr`)

---

## 0. Quick Reference

| 항목 | 값 |
|------|-----|
| 에이전트 명 | CIA (Content Ingestion Agent) |
| 구조 | 단일 에이전트 + 4개 스킬 |
| 핵심 게이트 | Human Confirm (필수) |
| DB | Supabase MCP (Project: `vvgghtpntxffysxijkxk`) |
| 대상 테이블 | events / notices / guides |
| 처리 단위 | 1건씩 (배치 모드 미지원) |
| 수정 루프 | 최대 5회 |
| 분류 모호 시 | confidence < 0.7 → 에스컬레이션 |

---

## 1. 작업 컨텍스트

### 1.1 배경
N잡크루 멤버스 허브의 콘텐츠(일정/공지/가이드) 입력을 관리자가 어드민 패널에서 수동 폼 작성으로 처리 중. 운영자가 raw 자료(이미지/스크린샷/메모)를 던지면 구조화·적재를 자동화하되, **DB 적재 직전 반드시 휴먼 컨펌**을 거치도록 한다.

### 1.2 목적
- 입력 시간 단축 (수동 폼 작성 → 대화형)
- 분류·필드 누락 실수 방지 (LLM 검증)
- 위험 차단 (컨펌 게이트로 잘못된 INSERT 방지)

### 1.3 범위

| 포함 | 제외 |
|------|------|
| events / notices / guides INSERT | UPDATE, DELETE |
| 이미지/텍스트/URL 입력 | members 테이블 (보안) |
| 컨펌 후 단건 적재 | 일괄 배치 적재 |

### 1.4 입출력 정의

| 항목 | 형식 |
|------|------|
| **입력** | 이미지(스크린샷, 사진), 텍스트 메모, URL, 캡처 + 짧은 지시문 |
| **중간 산출물** | `/output/staging/<timestamp>_<type>.json` (구조화 데이터) |
| **최종 산출물** | Supabase INSERT 결과 (id 반환) + `/output/log/<date>.md` (적재 로그) |

### 1.5 제약조건
- DB는 Supabase MCP로만 접근 (Project ID: `vvgghtpntxffysxijkxk`)
- 컨펌 없이 INSERT/UPDATE/DELETE 실행 절대 금지
- 1턴에 자료 1건씩 처리 (배치 미지원)
- 자료에 없는 필드는 추측 금지 → `null` 또는 "확인 필요" 표시
- 수정 루프 5회 초과 시 자동 취소 + 사유 로그

### 1.6 용어 정의

| 용어 | 의미 |
|------|------|
| **CIA** | Content Ingestion Agent (본 서브 에이전트) |
| **컨펌 게이트** | DB INSERT 직전 사용자 명시 승인 단계 |
| **Staging** | 컨펌 대기 중인 구조화 데이터 보관소 |
| **Raw Asset** | 사용자가 던진 원본 자료 (이미지/메모) |
| **에스컬레이션** | LLM 판단 보류 → 사용자에게 명시 확인 요청 |

---

## 2. 워크플로우 정의

### 2.1 전체 흐름도

```
[User: Raw Asset 투입]
       │
       ▼
┌─────────────────────────┐
│ Step 1: Intake & Classify│ ← [LLM 판단]
│   - 자료 수신             │
│   - 타입 분류             │
│   - 신뢰도 산출 (0.0-1.0) │
└──────────┬──────────────┘
           │
           ▼
   ┌───────────────┐
   │ confidence?   │ ← [LLM 자기 검증]
   └───┬───────┬───┘
       │ ≥0.7  │ <0.7
       │       └──────► [에스컬레이션] → User 확인 → Step 1 재진입
       ▼
┌─────────────────────────┐
│ Step 2: Extract & Validate│ ← [LLM + 스키마 검증]
│   - 필드 추출             │
│   - JSON 구조화           │
│   - 스키마 검증           │
└──────────┬──────────────┘
           │
           ▼
   ┌───────────────┐
   │ 스키마 통과?  │
   └───┬───────┬───┘
       │ Pass  │ Fail
       │       └──────► [자동 재시도 max 2회] → 실패 시 partial로 진행
       ▼
┌─────────────────────────┐
│ Step 3: Preview Generate│ ← [코드 + LLM]
│   - JSON 표시             │
│   - UI 미리보기 렌더       │
│   - 추측 필드 ⚠️ 표시      │
└──────────┬──────────────┘
           │
           ▼
┌═════════════════════════┐
║ Step 4: HUMAN CONFIRM   ║ ← [필수 게이트]
║   ✅ OK / ✏️ 수정 / ❌ 취소 ║
║   (수정 루프 max 5회)     ║
└══════════┬══════════════┘
           │ OK
           ▼
┌─────────────────────────┐
│ Step 5: DB Insert       │ ← [스크립트]
│   - Supabase MCP        │
│   - INSERT 실행          │
│   - ID 반환              │
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────┐
│ Step 6: Report & Log    │ ← [코드]
│   - 결과 리포트           │
│   - /output/log 기록      │
└─────────────────────────┘
```

### 2.2 단계별 명세

#### Step 1: Intake & Classify

| 항목 | 내용 |
|------|------|
| **수행 주체** | LLM |
| **입력** | 이미지/텍스트 + 사용자 지시문 |
| **출력** | `{type: "events|notices|guides", confidence: 0.0-1.0, reasoning: "..."}` |
| **성공 기준** | type ∈ {events, notices, guides} AND confidence ≥ 0.7 |
| **검증 방법** | LLM 자기 검증 (분류 근거 명시) |
| **실패 처리** | confidence < 0.7 → 에스컬레이션 (User에게 1회 확인) |

**분류 기준**:

| Type | 키워드 / 패턴 |
|------|--------------|
| events | 날짜, 마감, 시험, 보고, 시상, 교육일, MM/DD, YYYY-MM-DD |
| notices | 안내, 변경, 정책, 발표, 공지, "~을 알려드립니다" |
| guides | 절차, 방법, 매뉴얼, 단계, "~하는 법", 스크립트 |

#### Step 2: Extract & Validate

| 항목 | 내용 |
|------|------|
| **수행 주체** | LLM 추출 + 스크립트 검증 |
| **입력** | Raw Asset + type |
| **출력** | 타입별 JSON (스키마 준수) |
| **성공 기준** | 필수 필드 모두 존재, 타입 일치, enum 값 valid |
| **검증 방법** | JSON Schema 검증 (`validate_schema.py`) |
| **실패 처리** | 자동 재시도 max 2회 → 실패 시 partial 결과로 컨펌 단계 진입 (부족 필드 ⚠️ 마킹) |

**타입별 JSON 스키마**:

**events**:
```json
{
  "event_date": "YYYY-MM-DD (required)",
  "title": "string ≤200자 (required)",
  "description": "string",
  "tag": "t-imp | t-reg | t-ddl (required)",
  "tag_text": "중요 | 정기 | 마감 (auto-mapped)",
  "category": "exam|report|reward|education|meeting|sign|general (required)",
  "actions": ["string array (선택)"]
}
```

**notices**:
```json
{
  "icon": "emoji (default: 📢)",
  "icon_class": "i-blue|i-orange|i-green|i-purple|i-pink",
  "title": "string ≤200자 (required)",
  "author": "string (default: 멤버스 운영팀)",
  "body": "string (required, markdown 허용)"
}
```

**guides**:
```json
{
  "main_category": "njob | rebuild | faq (required)",
  "category": "서브카테고리명 (required)",
  "title": "string ≤200자 (required)",
  "description": "string 1-2줄 (required)",
  "badge": "b-new (default)",
  "badge_text": "NEW (default)",
  "steps": ["array of strings (required)"],
  "note": "핵심 포인트 (선택)",
  "copyable_text": "복붙용 카톡 문구 (선택)"
}
```

#### Step 3: Preview Generate

| 항목 | 내용 |
|------|------|
| **수행 주체** | LLM (Markdown 출력) |
| **입력** | 구조화 JSON |
| **출력** | 사용자용 미리보기 (JSON + UI 시뮬레이션 텍스트) |
| **성공 기준** | 모든 필드 표시, 추측/누락 필드 ⚠️ 마킹 |
| **검증 방법** | 규칙 기반 (필드 누락 체크) |
| **실패 처리** | 자동 재시도 1회 |

**미리보기 형식 (표준)**:
```
━━━━━━━━━━━━━━━━━━━━━━
📋 분류: [Type]
🎯 신뢰도: [0.0-1.0]
━━━━━━━━━━━━━━━━━━━━━━

[JSON 블록]

🔍 미리보기 (실제 화면 노출 시뮬):
[필드별 정리]

⚠️ 확인 필요:
- [추측한 필드 / 누락 필드 명시]

━━━━━━━━━━━━━━━━━━━━━━
다음 중 선택:
✅ "OK" / "ㄱㄱ" / "등록" → DB 적재
✏️ "수정: [필드명] [새 값]" → 재구성
❌ "취소" → 폐기
━━━━━━━━━━━━━━━━━━━━━━
```

#### Step 4: Human Confirm Gate ⚠️ 필수

| 항목 | 내용 |
|------|------|
| **수행 주체** | User |
| **입력** | 미리보기 |
| **출력** | 명시 응답 |
| **성공 기준** | User로부터 명시적 승인 키워드 수신 |
| **검증 방법** | 사람 검토 (필수) |
| **실패 처리** | 수정 요청 → Step 2 재진입 (최대 5회) → 초과 시 자동 취소 |

**컨펌 응답 키워드 (자연어 파싱)**:

| 의도 | 키워드 |
|------|--------|
| 승인 | OK, ok, ㄱㄱ, 고고, 등록, 진행, 좋아, 굿 |
| 수정 | 수정: [필드] [값], 바꿔, 변경 |
| 취소 | 취소, 폐기, 그만, 안할래 |

#### Step 5: DB Insert

| 항목 | 내용 |
|------|------|
| **수행 주체** | 스크립트 (Supabase MCP `execute_sql`) |
| **입력** | 컨펌된 JSON |
| **출력** | INSERT 결과 (returning id) |
| **성공 기준** | INSERT 성공 + id 반환 |
| **검증 방법** | DB 응답 확인 + 후속 SELECT로 row 존재 검증 |
| **실패 처리** | 자동 재시도 1회 → 실패 시 staging 파일 보존 + 에스컬레이션 |

#### Step 6: Report & Log

| 항목 | 내용 |
|------|------|
| **수행 주체** | 스크립트 |
| **입력** | INSERT 결과 |
| **출력** | 콘솔 리포트 + `/output/log/<date>.md` |
| **성공 기준** | 로그 파일 업데이트 |
| **검증 방법** | 파일 존재 확인 |
| **실패 처리** | 스킵 + 콘솔 경고 |

### 2.3 LLM 판단 vs 코드 처리 구분

| 단계 | LLM 판단 영역 | 코드 처리 영역 |
|------|-------------|--------------|
| 1 | 콘텐츠 타입 분류, 신뢰도 평가 | - |
| 2 | 필드 추출, 누락 판단, 자연어→구조 변환 | JSON Schema 검증 |
| 3 | 미리보기 텍스트 생성, 추측 필드 식별 | Markdown 포맷팅 |
| 4 | 컨펌 응답 의도 파싱 (자연어) | 키워드 매칭 백업 |
| 5 | - | Supabase INSERT, DB 응답 처리 |
| 6 | 로그 요약 문장 생성 | 파일 I/O |

### 2.4 상태 전이도

```
[idle]
  ├─(자료 수신)──> [classifying]
[classifying]
  ├─(confidence ≥ 0.7)──> [extracting]
  └─(confidence < 0.7)──> [awaiting_user_clarification] ─> [classifying]
[extracting]
  ├─(스키마 통과)──> [preview_ready]
  └─(재시도 2회 초과)──> [preview_ready (partial)]
[preview_ready]
  ├─(User: OK)──> [inserting]
  ├─(User: 수정, count < 5)──> [extracting]
  ├─(User: 수정, count ≥ 5)──> [cancelled (auto)]
  └─(User: 취소)──> [cancelled]
[inserting]
  ├─(성공)──> [done]
  └─(실패)──> [escalated]
[done] / [cancelled] / [escalated] ─> [idle]
```

---

## 3. 구현 스펙

### 3.1 폴더 구조

```
/njob-content-agent
  ├── CLAUDE.md                          # 메인 에이전트 (CIA 본체) 지침
  ├── /.claude
  │   ├── /skills
  │   │   ├── /content-classifier
  │   │   │   ├── SKILL.md               # 분류 로직 + 기준 표
  │   │   │   └── /references
  │   │   │       └── classification-rules.md
  │   │   ├── /field-extractor
  │   │   │   ├── SKILL.md               # 타입별 추출 로직
  │   │   │   ├── /scripts
  │   │   │   │   └── validate_schema.py # JSON 스키마 검증
  │   │   │   └── /references
  │   │   │       ├── schema-events.json
  │   │   │       ├── schema-notices.json
  │   │   │       └── schema-guides.json
  │   │   ├── /preview-renderer
  │   │   │   └── SKILL.md               # 미리보기 생성 가이드
  │   │   └── /supabase-inserter
  │   │       ├── SKILL.md               # INSERT 실행 가이드
  │   │       └── /scripts
  │   │           ├── insert_event.py
  │   │           ├── insert_notice.py
  │   │           └── insert_guide.py
  │   └── /agents
  │       └── (서브에이전트 분리 없음 - 단일 에이전트)
  ├── /output
  │   ├── /staging                       # 컨펌 대기 JSON
  │   └── /log                           # 일별 적재 로그
  └── /docs
      ├── PROJECT_CONTEXT.md             # 원본 프로젝트 컨텍스트
      └── DB_SCHEMA.md                   # DB 스키마 참조
```

### 3.2 에이전트 구조 결정

**채택: 단일 에이전트**

| 근거 | 설명 |
|------|------|
| 워크플로우 선형 | 분류→추출→컨펌→적재가 순차적, 분기 단순 |
| 컨텍스트 부담 적음 | 스킬 4개 합쳐도 토큰 부담 낮음 |
| 상태 추적 단순 | 한 대화 내 1건 처리 기준이라 메인이 직접 관리 가능 |
| 데이터 재전달 불필요 | 분류와 추출이 동일 Raw Asset 참조 |

**서브에이전트 미채택 이유**: 분리하면 컨텍스트 윈도우 절약 효과보다 데이터 재전달 오버헤드가 더 큼.

### 3.3 CLAUDE.md 핵심 섹션 목록

```
# CIA — N잡크루 콘텐츠 입력 에이전트

## 1. Role & Identity
## 2. Core Rules (Non-negotiable)
   - 컨펌 없이 INSERT 절대 금지
   - 추측 금지 (null 또는 "확인 필요" 표시)
   - 1건씩 처리
   - 수정 루프 max 5회
## 3. Workflow Overview (6 steps)
## 4. Skills Reference
   - content-classifier
   - field-extractor
   - preview-renderer
   - supabase-inserter
## 5. State Management
   - staging 파일 명명: stg_YYYYMMDD_HHMMSS_<type>.json
   - 로그 형식: YYYY-MM-DD.md
## 6. Supabase Connection
   - Project ID: vvgghtpntxffysxijkxk
   - MCP 도구 사용법
## 7. Confirmation Protocol
   - OK 키워드 목록
   - 수정 명령 파싱 규칙
   - 취소 처리
   - 수정 카운터 관리 (5회 초과 시 자동 취소)
## 8. Escalation Rules
   - 분류 confidence < 0.7
   - INSERT 재시도 실패
## 9. Output Format
## 10. Tone & Style
   - 한국어 90% + 영어 (기술 용어)
   - 짧고 직접적
   - 표/체크리스트 우선
## 11. Forbidden Patterns
   - 컨펌 우회
   - 추측 기반 필드 채우기
   - 일괄 처리 (배치 모드)
   - 사과/감탄사
```

### 3.4 스킬 파일 명세

| 스킬명 | 역할 | 트리거 조건 | 입력 | 출력 |
|--------|------|-----------|------|------|
| **content-classifier** | 자료→타입 분류 | Raw Asset 수신 시 (Step 1) | 이미지/텍스트 | `{type, confidence, reasoning}` |
| **field-extractor** | 타입별 필드 추출 + JSON 구조화 | 분류 완료 후 (Step 2) | Raw Asset + type | 타입별 JSON |
| **preview-renderer** | 사용자용 미리보기 생성 | JSON 완성 후 (Step 3) | 구조화 JSON | Markdown 미리보기 |
| **supabase-inserter** | DB INSERT 실행 | 컨펌 통과 후 (Step 5) | 컨펌된 JSON | INSERT 결과 (id) |

### 3.5 스크립트 명세

| 스크립트 | 역할 | 호출 시점 | 입출력 |
|---------|------|---------|------|
| `validate_schema.py` | JSON Schema 검증 | Step 2 검증 단계 | JSON → `{valid: bool, errors: []}` |
| `insert_event.py` | events 테이블 INSERT | Step 5 (type=events) | JSON → `{id, success}` |
| `insert_notice.py` | notices 테이블 INSERT | Step 5 (type=notices) | JSON → `{id, success}` |
| `insert_guide.py` | guides 테이블 INSERT | Step 5 (type=guides) | JSON → `{id, success}` |

### 3.6 산출물 파일 형식

**Staging JSON** (`/output/staging/stg_<timestamp>_<type>.json`):
```json
{
  "id": "stg_20260516_143022_events",
  "type": "events",
  "status": "awaiting_confirm | confirmed | inserted | cancelled",
  "raw_asset_summary": "11월 28일 자격시험 안내 캡처",
  "extracted_data": { /* 타입별 JSON */ },
  "uncertain_fields": ["actions"],
  "edit_count": 0,
  "created_at": "2026-05-16T14:30:22Z",
  "inserted_id": null
}
```

**Log** (`/output/log/2026-05-16.md`):
```markdown
# 적재 로그 2026-05-16

## 14:30 ✅ events #47
- title: N잡크루 자격시험
- 추측 필드: actions (사용자 컨펌)
- 수정 횟수: 1회

## 15:12 ❌ notices (취소)
- 사유: 사용자 취소 요청
- 수정 횟수: 0회

## 15:45 ⚠️ guides (에스컬레이션)
- 사유: INSERT 재시도 실패 (DB connection)
- staging 파일: stg_20260516_154500_guides.json
```

---

## 4. 검증·실패 처리 매트릭스

| 단계 | 검증 유형 | 실패 시 처리 | 최대 재시도 |
|------|---------|-----------|----------|
| 1. 분류 | LLM 자기 검증 | 에스컬레이션 | - |
| 2. 추출 | 스키마 검증 | 자동 재시도 → partial로 진행 | 2회 |
| 3. 미리보기 | 규칙 기반 | 자동 재시도 | 1회 |
| 4. 컨펌 | 사람 검토 | 수정 루프 → 5회 초과 시 자동 취소 | 5회 |
| 5. INSERT | DB 응답 확인 | 자동 재시도 → 에스컬레이션 | 1회 |
| 6. 로그 | 파일 존재 확인 | 스킵 + 경고 | - |

---

## 5. 데이터 전달 패턴

| 단계 간 전달 | 방식 | 이유 |
|-----------|------|------|
| 1 → 2 | 프롬프트 인라인 | 분류 결과만 전달 (작음) |
| 2 → 3 | 파일 기반 (`/output/staging/`) | JSON 구조화 데이터 (구조적) |
| 3 → 4 | 프롬프트 인라인 | 미리보기 텍스트만 표시 |
| 4 → 5 | 파일 기반 | staging 파일 그대로 사용 |
| 5 → 6 | 프롬프트 인라인 | INSERT 결과 (작음) |

---

## 6. 실행 체크리스트 (Claude Code 구현 시)

### Phase 1: 기본 구조
- [ ] `/njob-content-agent` 루트 디렉토리 생성
- [ ] `CLAUDE.md` 작성 (§3.3 섹션 기준)
- [ ] `/docs/PROJECT_CONTEXT.md` 복사 (원본 참조용)
- [ ] `/docs/DB_SCHEMA.md` 작성 (members.html 기준)

### Phase 2: 스킬 구축
- [ ] `content-classifier/SKILL.md` + `classification-rules.md`
- [ ] `field-extractor/SKILL.md` + 3개 schema JSON
- [ ] `field-extractor/scripts/validate_schema.py` 작성
- [ ] `preview-renderer/SKILL.md`
- [ ] `supabase-inserter/SKILL.md` + 3개 INSERT 스크립트

### Phase 3: 환경 설정
- [ ] Supabase MCP 연결 확인 (Project: `vvgghtpntxffysxijkxk`)
- [ ] `/output/staging/` 및 `/output/log/` 디렉토리 생성
- [ ] `.gitignore`에 `/output/staging/*.json` 추가 (선택)

### Phase 4: 테스트
- [ ] **events**: 더미 일정 이미지 1건 → 분류 → 컨펌 → INSERT → DB 확인
- [ ] **notices**: 더미 공지 텍스트 1건 → 동일 흐름
- [ ] **guides**: 더미 가이드 절차 1건 → 동일 흐름
- [ ] **수정 루프**: 5회 시도 → 자동 취소 동작 확인
- [ ] **취소 흐름**: User 취소 → staging 파일 status 업데이트 확인
- [ ] **에스컬레이션**: 분류 모호 케이스 → User 확인 요청 동작 확인
- [ ] **컨펌 우회 시도**: "그냥 등록해" 등 → 차단되는지 확인

### Phase 5: 운영 검증
- [ ] 로그 파일이 일별로 정상 생성되는지 확인
- [ ] 실제 운영 자료 5건 입력 후 정확도 평가
- [ ] 메인 페이지(`sfmi.members-center.co.kr`)에서 노출 확인

---

## 7. 합리적 Default 값 명세 (이번 설계 채택값)

| 항목 | 채택값 | 근거 |
|------|--------|------|
| 수정 루프 최대 횟수 | 5회 | 5회 이상 수정 = 입력 자료 자체가 부적합 → 자동 취소가 합리적 |
| 처리 단위 | 1건씩 | 컨펌 게이트의 효과 극대화, 멀티건 시 컨펌 피로도 증가 |
| 분류 모호 처리 | confidence < 0.7 → 에스컬레이션 | LLM 임의 판단보다 명시 확인이 안전, 0.7은 일반적 threshold |
| 분류 신뢰도 표시 | 미리보기에 항상 표시 | 사용자가 LLM 판단 품질 즉시 파악 가능 |
| INSERT 재시도 | 1회 | DB 일시 오류는 1회 재시도로 충분, 초과 시 인프라 이슈 |
| 추출 재시도 | 2회 | 스키마 누락은 LLM 재시도로 보완 가능, 3회 이상은 자료 부족 신호 |

---

## 8. 운영 시나리오 예시

### 시나리오 A: 정상 흐름 (events)
```
1. User: [캡처 이미지] + "11월 28일 자격시험"
2. CIA: 분류 → events (confidence 0.92)
3. CIA: 추출 → JSON 생성 → 미리보기 출력
4. User: "ㄱㄱ"
5. CIA: INSERT 실행 → id 47 반환
6. CIA: 로그 기록 → 완료 리포트
```

### 시나리오 B: 수정 루프 (notices)
```
1. User: [공지 이미지]
2. CIA: 분류 → notices (confidence 0.88)
3. CIA: 미리보기 (author: "운영팀")
4. User: "수정: author 멤버스 운영팀"
5. CIA: 재구성 → 미리보기 (edit_count: 1)
6. User: "OK"
7. CIA: INSERT → 완료
```

### 시나리오 C: 에스컬레이션 (분류 모호)
```
1. User: [텍스트만 있는 짧은 메모]
2. CIA: 분류 시도 → confidence 0.55
3. CIA: "다음 중 어떤 타입인가요? events / notices / guides"
4. User: "guides"
5. CIA: Step 2부터 재진입
```

### 시나리오 D: 자동 취소 (수정 5회 초과)
```
1-10. 수정 루프 5회 반복
11. CIA: "수정 시도 5회 초과 → 자동 취소. 자료를 정리 후 다시 시도해주세요."
12. CIA: staging 파일 status = cancelled, 로그 기록
```

---

## 9. 다음 단계 (Implementation Roadmap)

### Day 1
- Phase 1, 2 완료 (구조 + 스킬 파일 작성)

### Day 2
- Phase 3 (환경 설정) + Phase 4 일부 (events 테스트)

### Day 3
- Phase 4 완료 (전체 타입 + 예외 흐름 테스트)
- Phase 5 일부 (실 자료 3건)

### Day 4 이후
- 운영 투입 + 정확도 추적
- 필요 시 v1.1 patch (배치 모드, Rollback 등 추가 기능)

---

**END OF DESIGN DOCUMENT**

작성: Claude (claude-opus-4-7)
참조: members.html v1.0, PROJECT_CONTEXT.md
