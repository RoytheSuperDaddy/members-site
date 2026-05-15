# N잡크루 멤버스 허브 - 프로젝트 구조 & 셋업 가이드

## 최종 프로젝트 폴더 구조

```
members-site/                        ← 프로젝트 루트
│
├── index.html                       ← 메인 파일 (업로드한 새 버전)
├── CLAUDE.md                        ← 새 디자인 시스템 (실제 토큰 기반)
├── .mcp.json                        ← Supabase + GitHub MCP
├── .gitignore                       ← 시크릿/디버그 어셋 제외
├── README.md                        ← (선택) 프로젝트 설명
│
├── .github/
│   └── workflows/
│       └── claude.yml               ← GitHub Actions (@claude 멘션 등)
│
├── assets/                          ← 프로덕션 어셋 (18개, git 커밋)
│   ├── members-horizontal.png       ⭐ 메인 로고 (실사용)
│   ├── members-stack.png
│   ├── members-symbol.png
│   ├── members-symbol-t.png
│   ├── m-h.png, m-s.png, m-sy.png   ← 축약형
│   ├── njobcrew-ci.png              ⭐ N잡크루 CI
│   ├── njobcrew-symbol-t.png
│   ├── logo-njobcrew-ci.png
│   ├── rebuilding-horizontal.png    ⭐ 리빌딩 CI
│   ├── rebuilding-stack.png
│   ├── rebuilding-symbol.png
│   ├── rebuilding-symbol-t.png
│   ├── r-h.png, r-s.png, r-sy.png
│   └── samsungfire-ko.png           ← 삼성화재 모회사
│
├── fonts/                           ← 폰트 (별도 입수 필요)
│   ├── SamsungGothicLong-Regular.ttf    ⚠ 사용자가 별도 준비
│   └── SamsungGothicLong-UltraLight.ttf ⚠ 사용자가 별도 준비
│
└── assets-reference/                ← 디자인 참고용 (gitignore 제외)
    ├── _ref_members.png             ← 멤버스 디자인 reference
    ├── _ref_rebuilding.png          ← 리빌딩 디자인 reference
    ├── _font_test_bold.png          ← 폰트 테스트
    ├── _font_weights.png
    ├── _dbg_*.png                   ← 디버그 이미지 (4개)
    └── _debug_top1.png, _debug_top2.png
```

---

## Phase별 셋업 (이미 Phase 0-1 완료된 상태에서)

### Phase 2. 프로젝트 폴더 셋업 (15분)

#### 2-1. 저장소 위치로 이동

```powershell
cd $HOME\Projects\members-site
code .
```

저장소가 없다면 GitHub에서 먼저 `members-site` 생성 후:
```powershell
cd $HOME
mkdir Projects -Force
cd Projects
git clone https://github.com/<YOUR-ID>/members-site.git
cd members-site
code .
```

#### 2-2. 6개 핵심 파일을 루트에 배치

다운로드 폴더에서 PowerShell로 한 번에:

```powershell
cd $HOME\Projects\members-site

# 루트 파일들
Move-Item $HOME\Downloads\index.html .
Move-Item $HOME\Downloads\CLAUDE.md .
Move-Item $HOME\Downloads\.mcp.json .
Move-Item $HOME\Downloads\.gitignore .

# GitHub Actions
New-Item -ItemType Directory -Path ".github\workflows" -Force
Move-Item $HOME\Downloads\claude.yml .github\workflows\
```

#### 2-3. 어셋 폴더 압축 풀기

```powershell
# zip 풀기
Expand-Archive -Path $HOME\Downloads\N______Design_System.zip -DestinationPath . -Force

# 디버그/참고용 파일 분리
New-Item -ItemType Directory -Path "assets-reference" -Force
Move-Item assets\_*.png assets-reference\
```

이렇게 하면:
- `assets/` → 프로덕션 18개 (커밋 대상)
- `assets-reference/` → 디버그/참고 10개 (gitignore로 제외)

#### 2-4. 폰트 파일 준비 ⚠ 중요

```powershell
New-Item -ItemType Directory -Path "fonts" -Force
```

**삼성고딕(SamsungGothicLong) 폰트 파일을 `fonts/` 폴더에 배치 필요:**
- `SamsungGothicLong-Regular.ttf`
- `SamsungGothicLong-UltraLight.ttf`

> ⚠ 삼성화재 사내 폰트라 사용자가 별도 입수해야 함. 폰트가 없으면 `Noto Sans KR`로 자동 fallback (CSS `font-family: 'SamsungGL', 'Noto Sans KR', sans-serif` 우선순위).

만약 폰트 라이선스가 명확하지 않다면 일단 `index.html`의 `@font-face` 블록을 주석 처리하고 Noto Sans KR만 사용하는 것을 권장.

#### 2-5. 폴더 구조 검증

```powershell
tree /F /A
```

결과가 위 "최종 프로젝트 폴더 구조"와 일치하면 OK.

#### 2-6. Claude Code 첫 테스트

```powershell
claude
```

대화창에서 (새 토큰 기반 질문):
```
> CLAUDE.md를 읽고 답해줘:
  1. Primary 컬러(--p)와 Accent 컬러(--a) 값은?
  2. N잡크루와 리빌딩의 브랜드 컬러 분리 구조는?
  3. --gr-hero 그라데이션은 어떤 두 색을 잇나?
  4. 가이드 카드(.gc) 좌측 액센트 바는 카테고리별로 어떻게 다른가?
```

**예상 정답**:
1. `--p: #156BFF`, `--a: #00C8E5`
2. njob = `#003CDC` + sky `#5BC2E7`, rebuild = `#FF6A00` + sky `#FF9A4D`
3. `#156BFF → #00C8E5` (블루 → 시안)
4. `.is-njob` 진파랑 / `.is-rebuild` 오렌지 / `.is-faq` 그린

✅ 4개 다 맞으면 CLAUDE.md 로드 성공.

#### 2-7. Git commit 후 push

```powershell
git add .
git status   # 확인
git commit -m "feat: 디자인 시스템 v2 + 자동화 셋업"
git push origin main
```

---

### Phase 3. Vercel 자동 배포 연결 (5분)

이전과 동일:
1. [vercel.com](https://vercel.com) → GitHub OAuth 가입
2. Add New → Project → `members-site` 선택 → Import
3. Framework Preset: **Other**, Root Directory: `./`, Deploy
4. Settings → Domains → `sfmi.members-center.co.kr` 추가 → DNS 설정

이후 GitHub push마다 자동 배포 (2분 내 반영).

---

### Phase 4. GitHub Actions @claude 활성화 (10분)

이전과 동일:

1. **Anthropic API 키 발급**: console.anthropic.com → Create Key → 이름 `members-site-actions`
2. **GitHub Secret 등록**: 저장소 → Settings → Secrets and variables → Actions → New repository secret → `ANTHROPIC_API_KEY`
3. **Claude GitHub App 설치**:
   ```powershell
   cd $HOME\Projects\members-site
   claude
   > /install-github-app
   ```
4. **첫 @claude 테스트 Issue**:
   ```
   제목: [TEST] 챗봇 패널 디자인 점검
   본문:
   @claude
   index.html의 챗봇 패널(.chat-panel)을 점검해줘:
   1. CLAUDE.md 디자인 시스템 준수 여부
   2. --gr-hero 그라데이션을 chat-head에 적용했는지
   3. 14-15px 본문 폰트 사이즈 유지 여부
   ```

---

## 트러블슈팅

| 증상 | 원인 | 해결 |
|---|---|---|
| SamsungGL 폰트 미적용 | TTF 파일 누락 | `Noto Sans KR`로 fallback 자동 작동. 폰트 입수 후 `fonts/`에 배치 |
| `assets/members-horizontal.png` 깨짐 | zip 압축 풀기 오류 | `Expand-Archive` 재실행 또는 수동 압축해제 |
| `_dbg_*.png` 파일 git에 올라감 | `.gitignore` 미작동 | `git rm --cached assets/_*.png` 후 재커밋 |
| `index.html` 한글 깨짐 | UTF-8 BOM 누락 | VS Code 우하단 인코딩 → `UTF-8` 선택 후 저장 |
| Vercel 배포 후 이미지 안 보임 | 경로 대소문자 | Vercel은 case-sensitive. `Assets/` ≠ `assets/` |

---

## 다음 단계 체크리스트

- [ ] Phase 2-1: 저장소 폴더 확인
- [ ] Phase 2-2: 핵심 파일 6개 배치 (index.html, CLAUDE.md, .mcp.json, .gitignore, claude.yml)
- [ ] Phase 2-3: assets/ 압축 풀기 + 분류
- [ ] Phase 2-4: fonts/ 폴더 생성 (TTF 별도 입수)
- [ ] Phase 2-5: 폴더 구조 검증 (`tree /F /A`)
- [ ] Phase 2-6: CLAUDE.md 로드 테스트 4문항 통과
- [ ] Phase 2-7: Git commit + push
- [ ] Phase 3: Vercel 연결 + 도메인 설정
- [ ] Phase 4: Anthropic API 키 + GitHub Secret + Claude App
- [ ] Phase 4: 첫 @claude Issue 테스트

완료 후 본격 자동 개발 시작.
