# Skill: supabase-inserter

## Purpose

Human Confirm Gate 통과 후 Supabase MCP `execute_sql`을 사용하여 타입별 테이블에 INSERT를 실행하고, 결과 id를 반환한다.

## Trigger

CIA Step 5 — User가 명시적 승인 키워드 전달 후.

## Input

```json
{
  "type": "events | notices | guides",
  "extracted_data": { /* 컨펌된 타입별 JSON */ },
  "staging_id": "stg_20260516_143022_events"
}
```

## Output

```json
{
  "success": true,
  "inserted_id": 47,
  "table": "events",
  "staging_id": "stg_20260516_143022_events"
}
```

## Process

1. `scripts/insert_<type>.py`의 `build_insert_sql(data)`를 참조하여 INSERT SQL을 생성한다.
2. Supabase MCP `execute_sql`로 SQL을 실행한다:
   ```
   project_id: vvgghtpntxffysxijkxk
   query: [build_insert_sql 반환값]
   ```
3. 반환된 id로 `build_verify_sql(id)` SELECT를 실행하여 row 존재를 검증한다.
4. 성공 시 staging 파일 status를 `inserted`로 업데이트, `inserted_id` 기록.
5. 실패 시 재시도 1회 → 실패 시 에스컬레이션.

**자격증명**: 절대 하드코딩 금지. 환경 변수 또는 MCP 설정 참조.

## Success Criteria

- `execute_sql` 응답에서 `id` 추출 성공
- 후속 SELECT로 row 존재 확인

## Failure Handling

- INSERT 실패 → 자동 재시도 1회
- 재시도 실패 → staging 파일 보존 (status: `escalated`) + 메시지:
  ```
  ⚠️ DB INSERT 실패
  - staging 파일: [staging_id].json
  - 오류: [error message]
  - 관리자 수동 확인 필요
  ```

## Examples

**Example (events INSERT)**:
```
Supabase MCP execute_sql:
  project_id: vvgghtpntxffysxijkxk
  query: |
    INSERT INTO events (event_date, day_num, month_label, title, tag, tag_text, category)
    VALUES ('2026-11-28', 28, 'NOV', 'N잡크루 자격시험', 't-ddl', '마감', 'exam')
    RETURNING id;

결과: {"id": 47}

후속 검증:
  query: SELECT id FROM events WHERE id = 47;
  결과: row 존재 확인 → success
```
