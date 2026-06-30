"""
JSON Schema 검증 스크립트
호출: python validate_schema.py <type> <json_file_path>
      python validate_schema.py <type> --stdin  (stdin에서 JSON 읽기)
출력: stdout으로 {"valid": bool, "errors": []}

지원 타입: events, notices, guides
의존성: pip install jsonschema
"""

import json
import sys
from pathlib import Path

try:
    import jsonschema
    from jsonschema import validate, ValidationError
except ImportError:
    print(json.dumps({"valid": False, "errors": ["jsonschema 라이브러리 미설치: pip install jsonschema"]}))
    sys.exit(1)

SCHEMA_DIR = Path(__file__).parent.parent / "references"

VALID_TYPES = {"events", "notices", "guides"}


def load_schema(content_type: str) -> dict:
    schema_file = SCHEMA_DIR / f"schema-{content_type}.json"
    if not schema_file.exists():
        raise FileNotFoundError(f"스키마 파일 없음: {schema_file}")
    with open(schema_file, encoding="utf-8") as f:
        return json.load(f)


def validate_data(content_type: str, data: dict) -> dict:
    if content_type not in VALID_TYPES:
        return {
            "valid": False,
            "errors": [f"지원하지 않는 타입: {content_type}. 허용값: {sorted(VALID_TYPES)}"]
        }

    schema = load_schema(content_type)
    errors = []

    try:
        validate(instance=data, schema=schema)
    except ValidationError as e:
        # 첫 번째 오류만 아닌 전체 수집
        validator = jsonschema.Draft7Validator(schema)
        for error in sorted(validator.iter_errors(data), key=str):
            field = ".".join(str(p) for p in error.absolute_path) or "root"
            errors.append(f"{field}: {error.message}")

    return {"valid": len(errors) == 0, "errors": errors}


def main():
    if len(sys.argv) < 3:
        print("사용법: python validate_schema.py <type> <json_file_path>")
        print("       python validate_schema.py <type> --stdin")
        sys.exit(1)

    content_type = sys.argv[1].lower()
    source = sys.argv[2]

    try:
        if source == "--stdin":
            raw = sys.stdin.read()
            data = json.loads(raw)
        else:
            json_path = Path(source)
            if not json_path.exists():
                print(json.dumps({"valid": False, "errors": [f"파일 없음: {source}"]}))
                sys.exit(1)
            with open(json_path, encoding="utf-8") as f:
                payload = json.load(f)
            # staging 파일이면 extracted_data 추출
            data = payload.get("extracted_data", payload)

        result = validate_data(content_type, data)
        print(json.dumps(result, ensure_ascii=False))
        sys.exit(0 if result["valid"] else 1)

    except json.JSONDecodeError as e:
        print(json.dumps({"valid": False, "errors": [f"JSON 파싱 오류: {e}"]}))
        sys.exit(1)
    except FileNotFoundError as e:
        print(json.dumps({"valid": False, "errors": [str(e)]}))
        sys.exit(1)


if __name__ == "__main__":
    main()
