# Skill: field-extractor

## Purpose

분류된 타입(events/notices/guides)에 따라 Raw Asset에서 필드를 추출하여 타입별 JSON을 생성하고, JSON Schema로 검증한다.

## Trigger

CIA Step 2 — content-classifier 분류 완료 후 (또는 수정 루프 재진입 시).

## Input

- Raw Asset (이미지/텍스트)
- 분류 결과: `{type, confidence, reasoning}`
- 수정 시: 이전 extracted_data + 수정 명령

## Output

타입별 구조화 JSON + 검증 결과:

```json
{
  "extracted_data": { /* 타입별 JSON */ },
  "uncertain_fields": ["추측했거나 누락된 필드명"],
  "validation": { "valid": true, "errors": [] }
}
```

## Process

1. Raw Asset + type을 기반으로 타입별 스키마(`references/schema-<type>.json`)를 참조한다.
2. 자료에서 각 필드를 추출한다.
   - 자료에 명시된 값만 채운다.
   - 불분명한 필드: `null` 또는 `"확인 필요"` — 추측 금지
   - 추측한 경우: `uncertain_fields` 배열에 필드명 추가 + 이유 명시
3. `validate_schema.py`를 참조하여 JSON Schema 검증 로직을 수행한다.
4. 검증 실패 시 자동 재시도 (max 2회).
5. 2회 초과 실패 시 partial 결과로 Step 3 진입 (부족 필드 ⚠️ 마킹).

**자동 매핑 (코드 처리)**:
- `events.tag` → `tag_text`: t-imp→중요 / t-reg→정기 / t-ddl→마감
- `events.event_date` → `day_num`, `month_label`
- `guides.main_category` → `icon`, `icon_class`

## Success Criteria

- 필수 필드 모두 존재
- 타입 일치
- enum 값 유효
- `validation.valid = true`

## Failure Handling

- 스키마 검증 실패 → 자동 재시도 (max 2회)
- 2회 초과 → partial JSON으로 Step 3 진입
  - 부족/추측 필드에 `⚠️` 마킹
  - uncertain_fields에 명시

## Examples

**Example 1 (events)**:
```
입력: "11월 28일 N잡크루 자격시험, 마감일, category: exam"
출력:
{
  "extracted_data": {
    "event_date": "2026-11-28",
    "title": "N잡크루 자격시험",
    "description": null,
    "tag": "t-ddl",
    "tag_text": "마감",
    "category": "exam",
    "actions": null
  },
  "uncertain_fields": ["description", "actions"],
  "validation": { "valid": true, "errors": [] }
}
```

**Example 2 (guides)**:
```
입력: N잡크루 코드등록 절차 설명 텍스트
출력:
{
  "extracted_data": {
    "main_category": "njob",
    "category": "코드등록",
    "title": "N잡크루 코드등록 방법",
    "description": "확인 필요",
    "badge": "b-new",
    "badge_text": "NEW",
    "steps": ["1단계: ...", "2단계: ..."],
    "note": null,
    "copyable_text": null
  },
  "uncertain_fields": ["description"],
  "validation": { "valid": false, "errors": ["description: 확인 필요"] }
}
```
