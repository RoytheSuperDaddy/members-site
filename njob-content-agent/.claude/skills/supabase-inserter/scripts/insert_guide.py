"""
guides 테이블 INSERT용 SQL 생성기
실제 실행은 에이전트가 Supabase MCP execute_sql로 수행.

호출 예시:
  from insert_guide import build_insert_sql, build_verify_sql
  sql = build_insert_sql(data)
  verify_sql = build_verify_sql(inserted_id)
"""

from typing import Dict, List, Optional
import json

DEFAULT_BADGE = "b-new"
DEFAULT_BADGE_TEXT = "NEW"

ICON_MAP = {
    "njob": ("📋", "i-blue"),
    "rebuild": ("🔄", "i-orange"),
    "faq": ("❓", "i-green"),
}


def _escape(value: str) -> str:
    """SQL injection 방지: single quote 이스케이프"""
    if value is None:
        return "NULL"
    return value.replace("'", "''")


def _derive_icon(main_category: str):
    """main_category → (icon, icon_class) 자동 매핑"""
    return ICON_MAP.get(main_category, ("📋", "i-blue"))


def build_insert_sql(data: Dict) -> str:
    """검증된 guides JSON → INSERT SQL 문자열 반환 (RETURNING id 포함)"""
    main_category = data["main_category"]
    category = _escape(data["category"])
    title = _escape(data["title"])
    description = _escape(data["description"])
    badge = _escape(data.get("badge") or DEFAULT_BADGE)
    badge_text = _escape(data.get("badge_text") or DEFAULT_BADGE_TEXT)

    icon, icon_class = _derive_icon(main_category)
    icon = _escape(data.get("icon") or icon)
    icon_class = _escape(data.get("icon_class") or icon_class)

    steps = data.get("steps", [])
    steps_json = _escape(json.dumps(steps, ensure_ascii=False))

    note = data.get("note")
    note_sql = f"'{_escape(note)}'" if note else "NULL"

    copyable_text = data.get("copyable_text")
    copyable_sql = f"'{_escape(copyable_text)}'" if copyable_text else "NULL"

    return (
        f"INSERT INTO guides "
        f"(main_category, category, icon, icon_class, title, description, badge, badge_text, steps, note, copyable_text) "
        f"VALUES ("
        f"'{main_category}', '{category}', '{icon}', '{icon_class}', '{title}', '{description}', "
        f"'{badge}', '{badge_text}', '{steps_json}'::jsonb, {note_sql}, {copyable_sql}"
        f") RETURNING id;"
    )


def build_verify_sql(inserted_id: int) -> str:
    """INSERT 후 row 존재 확인 SELECT"""
    return f"SELECT id, title, main_category FROM guides WHERE id = {inserted_id};"
