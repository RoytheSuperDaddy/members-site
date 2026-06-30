# Claude Code 1-Shot 프롬프트

> Claude Code 터미널에서 즉시 사용. 아래 블록 전체 복사 → 붙여넣기

---

```
첨부된 2개 문서를 기반으로 N잡크루 콘텐츠 자동 입력 에이전트(CIA) 전체 구조를 생성해줘.

[필수 첨부]
1. njob-content-agent-design.md — 마스터 설계서
2. CLAUDE_CODE_EXECUTION_ORDER.md — 실행 지시서

[작업 범위]
- 루트 경로: ./njob-content-agent
- 폴더 구조 + 모든 파일 생성
- CLAUDE.md, 4개 SKILL.md, 3개 JSON schema, 4개 Python 스크립트
- docs/DB_SCHEMA.md 포함

[준수 사항]
- 설계서 명세를 정확히 따를 것 (확장/추측 금지)
- 컨펌 게이트 우회 로직 절대 금지
- Supabase 자격증명 하드코딩 금지 → 환경변수 참조
- 설계서에 없는 기능은 TODO 주석으로 표시

[완료 후 보고]
- 생성된 파일 트리
- Definition of Done 체크리스트 결과
- 첫 테스트 시나리오 (events 1건) 실행 안내

시작해줘.
```

---

## 사용 방법

1. Claude Code 실행: `claude` (또는 사용 중인 CLI 명령)
2. 작업 디렉토리로 이동: `cd ~/projects` (원하는 경로)
3. 다음 2개 파일을 작업 디렉토리에 복사:
   - `njob-content-agent-design.md`
   - `CLAUDE_CODE_EXECUTION_ORDER.md`
4. 위 프롬프트 블록 복사 → Claude Code에 붙여넣기

## 실행 후 확인

```bash
cd ./njob-content-agent
tree -L 4
# 또는
find . -type f | sort
```

체크리스트와 일치하는지 확인.
