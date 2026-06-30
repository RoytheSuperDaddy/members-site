"""
events 테이블 INSERT용 SQL 생성기
실제 실행은 에이전트가 Supabase MCP execute_sql로 수행.

호출 예시:
  from insert_event import build_insert_sql, build_verify_sql
  sql = build_insert_sql(data)
  verify_sql = build_verify_sql(inserted_id)
"""

from typing import Dict, List, Optional
import json

MONTH_LABELS = [
    "JAN", "FEB", "MAR", "APR", "MAY", "JUN",
    "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"
]

TAG_TEXT_MAP = {
    "t-imp": "중요",
    "t-reg": "정기",
    "t-ddl": "마감",
}


def _escape(value: str) -> str:
    """SQL injection 방지: single quote 이스케이프"""
    if value is None:
        return "NULL"
    return value.replace("'", "''")


def _derive_day_num(event_date: str) -> int:
    """YYYY-MM-DD에서 day 추출"""
    return int(event_date.split("-")[2])


def _derive_month_label(event_date: str) -> str:
    """YYYY-MM-DD에서 month label 추출"""
    month_idx = int(event_date.split("-")[1]) - 1
    return MONTH_LABELS[month_idx]


def build_insert_sql(data: Dict) -> str:
    """검증된 events JSON → INSERT SQL 문자열 반환 (RETURNING id 포함)"""
    event_date = data["event_date"]
    day_num = _derive_day_num(event_date)
    month_label = _derive_month_label(event_date)
    title = _escape(data["title"])
    tag = _escape(data["tag"])
    tag_text = _escape(TAG_TEXT_MAP.get(data["tag"], data.get("tag_text", "")))
    category = _escape(data["category"])

    description = data.get("description")
    desc_sql = f"'{_escape(description)}'" if description else "NULL"

    actions = data.get("actions")
    if actions and isinstance(actions, list):
        actions_json = _escape(json.dumps(actions, ensure_ascii=False))
        actions_sql = f"'{actions_json}'::jsonb"
    else:
        actions_sql = "NULL"

    return (
        f"INSERT INTO events "
        f"(event_date, day_num, month_label, title, description, tag, tag_text, category, actions) "
        f"VALUES ("
        f"'{event_date}', {day_num}, '{month_label}', '{title}', "
        f"{desc_sql}, '{tag}', '{tag_text}', '{category}', {actions_sql}"
        f") RETURNING id;"
    )


def build_verify_sql(inserted_id: int) -> str:
    """INSERT 후 row 존재 확인 SELECT"""
    return f"SELECT id, title, event_date FROM events WHERE id = {inserted_id};"
