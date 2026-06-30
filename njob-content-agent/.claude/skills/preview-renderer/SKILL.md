# Skill: preview-renderer

## Purpose

field-extractor의 구조화 JSON을 받아 사용자가 검토할 수 있는 Markdown 미리보기를 생성한다. 추측/누락 필드를 ⚠️로 명시하고, 컨펌 선택지를 제시한다.

## Trigger

CIA Step 3 — field-extractor JSON 완성 후 (또는 수정 루프 재진입 시).

## Input

```json
{
  "type": "events | notices | guides",
  "confidence": 0.92,
  "extracted_data": {},
  "uncertain_fields": [],
  "edit_count": 0
}
```

## Output

다음 표준 형식의 Markdown 텍스트:

```
━━━━━━━━━━━━━━━━━━━━━━
📋 분류: [type]
🎯 신뢰도: [confidence]
✏️ 수정 횟수: [edit_count]/5
━━━━━━━━━━━━━━━━━━━━━━

[JSON 블록]

🔍 미리보기 (실제 화면 노출 시뮬):
[타입별 필드 정리]

⚠️ 확인 필요:
- [uncertain_fields 목록 또는 "없음"]

━━━━━━━━━━━━━━━━━━━━━━
✅ "OK" / "ㄱㄱ" / "등록" → DB 적재
✏️ "수정: [필드명] [새 값]" → 재구성
❌ "취소" → 폐기
━━━━━━━━━━━━━━━━━━━━━━
```

## Process

1. type별 미리보기 포맷을 적용한다.
2. uncertain_fields가 있으면 각 항목을 ⚠️ 접두사로 표시한다.
3. null 값 필드는 `(없음)` 또는 `(확인 필요)`로 표시한다.
4. edit_count를 항상 표시한다 (수정 잔여 횟수 계산: 5 - edit_count).
5. 컨펌 선택지를 항상 하단에 포함한다.

**타입별 미리보기 포맷**:

**events**:
```
📅 날짜: [event_date]  |  🏷️ 태그: [tag_text]  |  📁 카테고리: [category]
📌 제목: [title]
📝 설명: [description]
⚡ 액션: [actions 각 항목]
```

**notices**:
```
[icon] 제목: [title]
👤 작성자: [author]
📄 내용:
[body]
```

**guides**:
```
📂 [main_category] > [category]
📌 제목: [title]
📝 요약: [description]
🏷️ 뱃지: [badge_text]
📋 단계:
  1. [step 1]
  2. [step 2]
  ...
💡 핵심: [note]
📋 카톡 문구: [copyable_text]
```

## Success Criteria

- 모든 필드 표시 (null 포함)
- uncertain_fields 항목 ⚠️ 마킹
- 컨펌 선택지 포함
- edit_count 표시

## Failure Handling

- 출력 생성 실패 → 자동 재시도 1회
- 재시도 실패 → raw JSON + 기본 선택지만 출력 (partial 미리보기)

## Examples

**Example 1 (events)**:
```
━━━━━━━━━━━━━━━━━━━━━━
📋 분류: events
🎯 신뢰도: 0.92
✏️ 수정 횟수: 0/5
━━━━━━━━━━━━━━━━━━━━━━

{
  "event_date": "2026-11-28",
  "title": "N잡크루 자격시험",
  "description": null,
  "tag": "t-ddl",
  "tag_text": "마감",
  "category": "exam",
  "actions": null
}

🔍 미리보기:
📅 날짜: 2026-11-28  |  🏷️ 태그: 마감  |  📁 카테고리: exam
📌 제목: N잡크루 자격시험
📝 설명: (없음)
⚡ 액션: (없음)

⚠️ 확인 필요:
- description: 원본 자료에 명시 없음
- actions: 원본 자료에 명시 없음

━━━━━━━━━━━━━━━━━━━━━━
✅ "OK" / "ㄱㄱ" / "등록" → DB 적재
✏️ "수정: [필드명] [새 값]" → 재구성
❌ "취소" → 폐기
━━━━━━━━━━━━━━━━━━━━━━
```
