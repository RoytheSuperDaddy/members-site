# Claude Code 실행 지시서

> 이 파일과 `njob-content-agent-design.md`를 함께 Claude Code에 전달하세요.

---

## 🎯 Mission

첨부된 `njob-content-agent-design.md` 설계서에 따라 **N잡크루 콘텐츠 자동 입력 에이전트(CIA)** 의 전체 폴더 구조와 파일을 생성한다.

---

## 📋 실행 순서

### Phase 1: 구조 생성

다음 폴더 구조를 정확히 생성하라:

```
/njob-content-agent
  ├── CLAUDE.md
  ├── .claude/
  │   ├── skills/
  │   │   ├── content-classifier/
  │   │   │   ├── SKILL.md
  │   │   │   └── references/
  │   │   │       └── classification-rules.md
  │   │   ├── field-extractor/
  │   │   │   ├── SKILL.md
  │   │   │   ├── scripts/
  │   │   │   │   └── validate_schema.py
  │   │   │   └── references/
  │   │   │       ├── schema-events.json
  │   │   │       ├── schema-notices.json
  │   │   │       └── schema-guides.json
  │   │   ├── preview-renderer/
  │   │   │   └── SKILL.md
  │   │   └── supabase-inserter/
  │   │       ├── SKILL.md
  │   │       └── scripts/
  │   │           ├── insert_event.py
  │   │           ├── insert_notice.py
  │   │           └── insert_guide.py
  ├── output/
  │   ├── staging/
  │   │   └── .gitkeep
  │   └── log/
  │       └── .gitkeep
  └── docs/
      ├── PROJECT_CONTEXT.md
      └── DB_SCHEMA.md
```

### Phase 2: 파일 작성 규칙

각 파일 작성 시 **반드시 설계서의 해당 섹션을 참조**할 것:

| 파일 | 설계서 참조 섹션 |
|------|---------------|
| `CLAUDE.md` | §3.3 (CLAUDE.md 핵심 섹션 목록) |
| `content-classifier/SKILL.md` | §2.2 Step 1 + 분류 기준 표 |
| `field-extractor/SKILL.md` | §2.2 Step 2 + 타입별 스키마 |
| `field-extractor/references/schema-*.json` | §2.2 Step 2 JSON 스키마 |
| `preview-renderer/SKILL.md` | §2.2 Step 3 + 미리보기 형식 표준 |
| `supabase-inserter/SKILL.md` | §2.2 Step 5 |
| `docs/DB_SCHEMA.md` | 아래 §부록 A |

### Phase 3: 각 파일 작성 가이드

#### 3.1 `CLAUDE.md` 작성 지침

다음 11개 섹션을 모두 포함:
1. Role & Identity
2. Core Rules (Non-negotiable) — 4개 룰 명시
3. Workflow Overview — 6 steps 다이어그램 포함
4. Skills Reference — 4개 스킬 호출 조건
5. State Management — staging/log 명명 규칙
6. Supabase Connection — Project ID `vvgghtpntxffysxijkxk`
7. Confirmation Protocol — OK/수정/취소 키워드 표
8. Escalation Rules — 분류 confidence < 0.7, INSERT 실패
9. Output Format
10. Tone & Style — 한국어 90% + 짧고 직접적
11. Forbidden Patterns

**Tone 예시 포함**: "도움이 되셨길~" 같은 멘트 금지, 짧고 직접적, 표/체크리스트 우선

#### 3.2 스킬 SKILL.md 공통 구조

```markdown
# Skill: [이름]

## Purpose
[목적 1-2줄]

## Trigger
[언제 호출되는가]

## Input
[입력 형식]

## Output
[출력 형식]

## Process
[단계별 처리 로직]

## Success Criteria
[성공 기준]

## Failure Handling
[실패 시 처리]

## Examples
[입출력 예시 1-2개]
```

#### 3.3 JSON Schema 작성 (`schema-events.json` 예시)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["event_date", "title", "tag", "category"],
  "properties": {
    "event_date": {
      "type": "string",
      "pattern": "^\\d{4}-\\d{2}-\\d{2}$"
    },
    "title": {
      "type": "string",
      "maxLength": 200
    },
    "description": { "type": "string" },
    "tag": {
      "type": "string",
      "enum": ["t-imp", "t-reg", "t-ddl"]
    },
    "tag_text": {
      "type": "string",
      "enum": ["중요", "정기", "마감"]
    },
    "category": {
      "type": "string",
      "enum": ["exam", "report", "reward", "education", "meeting", "sign", "general"]
    },
    "actions": {
      "type": "array",
      "items": { "type": "string" }
    }
  }
}
```

`schema-notices.json`, `schema-guides.json`도 설계서 §2.2 Step 2 스키마 기준으로 동일 패턴 작성.

#### 3.4 `validate_schema.py` 작성

```python
"""
JSON Schema 검증 스크립트
호출: python validate_schema.py <type> <json_file_path>
출력: stdout으로 {"valid": bool, "errors": []}
"""
import json
import sys
from pathlib import Path

# jsonschema 라이브러리 사용
# pip install jsonschema

SCHEMA_DIR = Path(__file__).parent.parent / "references"

def validate(content_type: str, data: dict) -> dict:
    schema_file = SCHEMA_DIR / f"schema-{content_type}.json"
    # ... 구현
    pass

if __name__ == "__main__":
    # CLI 인터페이스
    pass
```

#### 3.5 INSERT 스크립트 (`insert_event.py` 예시)

Supabase MCP를 직접 호출하지 말고, **에이전트가 호출할 SQL을 반환**하는 helper로 작성:

```python
"""
events 테이블 INSERT용 SQL 생성기
실제 실행은 에이전트가 Supabase MCP execute_sql로 수행
"""
import json
from typing import Dict

def build_insert_sql(data: Dict) -> str:
    """검증된 JSON → INSERT SQL 문자열 반환"""
    # SQL injection 방지: 파라미터 escaping
    # RETURNING id 포함
    pass

def build_verify_sql(inserted_id: int) -> str:
    """INSERT 후 row 존재 확인 SELECT"""
    pass
```

### Phase 4: docs 파일 작성

#### `docs/PROJECT_CONTEXT.md`
원본 PROJECT_CONTEXT.md를 그대로 복사 (사용자가 직접 제공)

#### `docs/DB_SCHEMA.md`
아래 §부록 A 내용 사용

---

## 📚 부록 A: DB_SCHEMA.md 내용

```markdown
# DB Schema Reference

Supabase Project: `vvgghtpntxffysxijkxk`

## events
| Column | Type | Required | Notes |
|--------|------|----------|-------|
| id | BIGINT (PK) | auto | 자동 증가 |
| event_date | DATE | ✓ | 일정 날짜 |
| day_num | INT | auto | event_date에서 추출 |
| month_label | VARCHAR(10) | auto | JAN~DEC |
| title | VARCHAR(200) | ✓ | 업무명 |
| description | TEXT | - | 상세 |
| tag | VARCHAR(20) | ✓ | t-imp / t-reg / t-ddl |
| tag_text | VARCHAR(20) | auto | 중요 / 정기 / 마감 (tag 매핑) |
| category | VARCHAR(30) | ✓ | exam/report/reward/education/meeting/sign/general |
| actions | JSONB | - | 액션 항목 배열 |

## notices
| Column | Type | Required | Notes |
|--------|------|----------|-------|
| id | BIGINT (PK) | auto | |
| icon | VARCHAR(10) | - | default: 📢 |
| icon_class | VARCHAR(20) | - | i-blue/i-orange/i-green/i-purple/i-pink |
| title | VARCHAR(200) | ✓ | |
| author | VARCHAR(50) | - | default: 멤버스 운영팀 |
| body | TEXT | ✓ | markdown 허용 |

## guides
| Column | Type | Required | Notes |
|--------|------|----------|-------|
| id | BIGINT (PK) | auto | |
| main_category | VARCHAR(20) | ✓ | njob/rebuild/faq |
| category | VARCHAR(20) | ✓ | 서브카테고리 |
| icon | VARCHAR(10) | - | main_category 기반 자동 |
| icon_class | VARCHAR(20) | - | main_category 기반 자동 |
| title | VARCHAR(200) | ✓ | |
| description | TEXT | ✓ | |
| badge | VARCHAR(20) | - | b-new (default) |
| badge_text | VARCHAR(20) | - | NEW (default) |
| steps | JSONB | ✓ | 단계 배열 |
| note | TEXT | - | 핵심 포인트 |
| copyable_text | TEXT | - | 복붙용 카톡 문구 |

## 자동 매핑 룰

### events.tag → tag_text
- t-imp → 중요
- t-reg → 정기
- t-ddl → 마감

### events.event_date → day_num, month_label
- day_num: event_date의 day 부분
- month_label: ['JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC']

### guides.main_category → icon, icon_class
| main_category | icon | icon_class |
|---------------|------|-----------|
| njob | 📋 | i-blue |
| rebuild | 🔄 | i-orange |
| faq | ❓ | i-green |
```

---

## ✅ 완료 기준 (Definition of Done)

체크리스트 모두 통과 시 완료:

- [ ] 폴더 구조가 §Phase 1과 정확히 일치
- [ ] 모든 SKILL.md가 §3.2 공통 구조 준수
- [ ] CLAUDE.md에 11개 섹션 모두 포함
- [ ] 3개 JSON Schema 파일이 설계서 §2.2 Step 2 스키마와 일치
- [ ] `validate_schema.py` 단독 실행 가능 (CLI 인터페이스)
- [ ] 3개 INSERT 스크립트가 SQL 문자열 반환 가능
- [ ] `output/staging`, `output/log` 디렉토리 존재 + `.gitkeep`
- [ ] `docs/DB_SCHEMA.md` 작성 완료

---

## 🚨 주의사항

1. **설계서를 임의 해석/확장하지 말 것** — 설계서에 명시된 내용만 구현
2. **컨펌 게이트 우회 로직 절대 금지** — INSERT 직전 컨펌 필수
3. **추측 코드 금지** — 설계서에 없는 기능은 TODO 주석으로 표시
4. **Supabase 자격증명 하드코딩 금지** — 환경 변수 또는 MCP 설정 참조
5. **모든 한국어 텍스트 UTF-8 인코딩 보장**

---

## 📤 출력 형식

작업 완료 후 다음을 보고:

```markdown
## 생성 결과
- 총 파일 수: [N]개
- 폴더: [N]개
- 코드 라인: [N]줄

## 파일별 상태
[파일 경로 + 상태 표]

## 검증 결과
[Definition of Done 체크리스트 결과]

## 다음 단계
[Phase 4 테스트 시나리오 제안]
```

---

**END OF EXECUTION ORDER**
