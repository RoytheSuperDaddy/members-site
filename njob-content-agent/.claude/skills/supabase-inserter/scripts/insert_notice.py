"""
notices 테이블 INSERT용 SQL 생성기
실제 실행은 에이전트가 Supabase MCP execute_sql로 수행.

호출 예시:
  from insert_notice import build_insert_sql, build_verify_sql
  sql = build_insert_sql(data)
  verify_sql = build_verify_sql(inserted_id)
"""

from typing import Dict, Optional

DEFAULT_ICON = "📢"
DEFAULT_AUTHOR = "멤버스 운영팀"
DEFAULT_ICON_CLASS = "i-blue"


def _escape(value: str) -> str:
    """SQL injection 방지: single quote 이스케이프"""
    if value is None:
        return "NULL"
    return value.replace("'", "''")


def build_insert_sql(data: Dict) -> str:
    """검증된 notices JSON → INSERT SQL 문자열 반환 (RETURNING id 포함)"""
    icon = _escape(data.get("icon") or DEFAULT_ICON)
    icon_class = _escape(data.get("icon_class") or DEFAULT_ICON_CLASS)
    title = _escape(data["title"])
    author = _escape(data.get("author") or DEFAULT_AUTHOR)
    body = _escape(data["body"])

    return (
        f"INSERT INTO notices (icon, icon_class, title, author, body) "
        f"VALUES ("
        f"'{icon}', '{icon_class}', '{title}', '{author}', '{body}'"
        f") RETURNING id;"
    )


def build_verify_sql(inserted_id: int) -> str:
    """INSERT 후 row 존재 확인 SELECT"""
    return f"SELECT id, title, author FROM notices WHERE id = {inserted_id};"
