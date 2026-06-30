# Skill: content-classifier

## Purpose

Raw Asset(이미지/텍스트/URL)을 수신하여 콘텐츠 타입(events/notices/guides)을 분류하고 신뢰도(confidence)를 산출한다.

## Trigger

CIA Step 1 — Raw Asset 수신 직후 호출.

## Input

- 이미지, 텍스트 메모, URL, 또는 복합 자료
- 사용자 지시문 (선택)

## Output

```json
{
  "type": "events | notices | guides",
  "confidence": 0.0,
  "reasoning": "분류 근거 1-2줄"
}
```

## Process

1. Raw Asset 전체를 읽는다.
2. 아래 분류 기준 표와 `references/classification-rules.md`를 참조한다.
3. 가장 부합하는 type을 선택하고 confidence(0.0~1.0)를 산출한다.
4. reasoning에 분류 근거를 명시한다.
5. confidence < 0.7이면 에스컬레이션(사용자에게 확인 요청).

**분류 기준**:

| Type | 키워드 / 패턴 |
|------|-------------|
| events | 날짜, 마감, 시험, 보고, 시상, 교육일, MM/DD, YYYY-MM-DD, 일정, 기한 |
| notices | 안내, 변경, 정책, 발표, 공지, "~을 알려드립니다", 시행, 변경사항 |
| guides | 절차, 방법, 매뉴얼, 단계, "~하는 법", 스크립트, 가이드, 순서 |

## Success Criteria

- `type` ∈ {events, notices, guides}
- `confidence` ≥ 0.7
- `reasoning` 비어있지 않음

## Failure Handling

- confidence < 0.7 → 에스컬레이션 메시지 출력:
  ```
  분류 신뢰도 부족 (confidence: [값])
  다음 중 타입을 직접 선택해주세요:
  1. events (날짜/일정 관련)
  2. notices (공지/안내 관련)
  3. guides (절차/매뉴얼 관련)
  ```
- 사용자 응답 후 Step 1 재진입

## Examples

**Example 1**:
```
입력: "11월 28일 N잡크루 자격시험 안내" + 캡처 이미지
출력:
{
  "type": "events",
  "confidence": 0.92,
  "reasoning": "명확한 날짜(11월 28일) + 시험 키워드 존재. events 분류."
}
```

**Example 2**:
```
입력: "수수료 정책 변경 안내드립니다"
출력:
{
  "type": "notices",
  "confidence": 0.88,
  "reasoning": "정책 변경 + 안내 키워드. notices 분류."
}
```

**Example 3 (에스컬레이션)**:
```
입력: "이거 참고해서 진행해주세요"
출력:
{
  "type": null,
  "confidence": 0.45,
  "reasoning": "타입 판별 키워드 부재. 에스컬레이션 필요."
}
```
