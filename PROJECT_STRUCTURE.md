# N잡크루 멤버스 허브 - 프로젝트 구조

## 최종 폴더 구조

```
members-site/                          ← 프로젝트 루트 (= GitHub 저장소)
│
├── index.html                         ← 메인 파일 (서비스 본체, 단일 HTML)
├── CLAUDE.md                          ← Claude Code 자동 로드 디자인 시스템 ⭐
├── PROJECT_CONTEXT.md                 ← (선택) 추가 컨텍스트 문서
├── .mcp.json                          ← Supabase + GitHub MCP 연동
├── .gitignore                         ← 민감정보 차단
│
├── assets/                            ← 이미지 어셋 (12개)
│   ├── members-horizontal.png         ← 메인 로고 (5곳에서 참조)
│   ├── members-stack.png
│   ├── members-symbol.png
│   ├── members-symbol-t.png
│   ├── rebuilding-horizontal.png      ← 리빌딩 사업부 로고
│   ├── rebuilding-stack.png
│   ├── rebuilding-symbol.png
│   ├── rebuilding-symbol-t.png
│   ├── njobcrew-ci.png                ← N잡크루 CI
│   ├── logo-njobcrew-ci.png
│   ├── njobcrew-symbol-t.png
│   └── samsungfire-ko.png             ← 삼성화재 상위 CI
│
├── fonts/                             ← 로컬 폰트 파일
│   ├── SamsungGothicLong-Regular.ttf  ← (직접 구해서 배치 필요)
│   ├── SamsungGothicLong-UltraLight.ttf
│   └── README.md                      ← 폰트 출처 + 라이선스 안내
│
└── .github/
    └── workflows/
        └── claude.yml                 ← GitHub Actions 자동화
                                          (@claude 멘션 / PR 리뷰 / Cron / 수동)
```

## 파일 역할 매트릭스

| 파일/폴더 | 역할 | Git 포함 | 비고 |
|---|---|---|---|
| `index.html` | 서비스 본체 | ✅ | 모든 화면 + Vanilla JS + 인라인 CSS |
| `CLAUDE.md` | 디자인 시스템 자동 로드 | ✅ | Claude Code가 매 세션 자동 인지 |
| `.mcp.json` | MCP 서버 정의 | ✅ | Supabase 직접 SQL 실행 가능 |
| `.gitignore` | 보안 차단 | ✅ | `.env*` 제외 처리 |
| `assets/` | 이미지 어셋 | ✅ | Vercel 배포 시 함께 서빙 |
| `fonts/*.ttf` | 폰트 | ✅ | 폰트 라이선스 확인 후 포함 |
| `.github/workflows/` | CI/CD | ✅ | GitHub Actions 트리거 |
| `.env.local` | 로컬 비밀키 | ❌ | gitignore 처리 |

## 배포 후 도메인 URL 구조

```
sfmi.members-center.co.kr/
├── /                          → index.html
├── /assets/members-horizontal.png  → 로고 이미지
└── /fonts/SamsungGothicLong-Regular.ttf  → 폰트
```

## 폴더 배치 체크리스트 (Windows)

PowerShell에서:

```powershell
cd $HOME\Projects\members-site

# 1. 핵심 파일 4개 루트에 배치
Move-Item $HOME\Downloads\CLAUDE.md .
Move-Item $HOME\Downloads\.mcp.json .
Move-Item $HOME\Downloads\.gitignore .
Move-Item $HOME\Downloads\index.html .       # 업로드 받은 새 버전

# 2. assets 폴더 생성 + 이미지 12개 배치
New-Item -ItemType Directory -Path "assets" -Force
Move-Item $HOME\Downloads\assets\*.png .\assets\

# 3. fonts 폴더 생성 + (폰트는 별도 입수)
New-Item -ItemType Directory -Path "fonts" -Force
Move-Item $HOME\Downloads\fonts\README.md .\fonts\

# 4. .github/workflows 폴더 생성 + workflow 파일 배치
New-Item -ItemType Directory -Path ".github\workflows" -Force
Move-Item $HOME\Downloads\claude.yml .\.github\workflows\

# 5. 구조 확인
tree /F /A
```

## 첫 commit/push

```powershell
git add .
git status   # 모든 파일 확인
git commit -m "feat: 디자인 시스템 v2 + Claude Code 자동화 셋업

- Brand-Forward 이중 브랜드 디자인 시스템 적용
- assets 12종 + fonts 폴더 구조
- CLAUDE.md (Claude Code 자동 로드)
- GitHub Actions @claude 자동화
- Supabase MCP 연동"

git push origin main
```

## Vercel 자동 배포 시 주의

Vercel 프로젝트 설정에서:
- **Framework Preset**: Other (정적 HTML)
- **Build Command**: (비워두기)
- **Output Directory**: `./` (루트 자체)
- **Install Command**: (비워두기)

→ 단일 HTML + 정적 어셋만 있으므로 빌드 없이 그대로 서빙.

## Claude Code 동작 확인 (Step 4)

새 CLAUDE.md 기반의 테스트 질문:

```
> CLAUDE.md를 읽고 답해줘:
  1. Primary 컬러(--p)와 Accent 컬러(--a) 값은?
  2. N잡크루와 리빌딩의 브랜드 컬러는 각각 어떻게 다른가?
  3. --gr-hero 그라데이션은 어떤 두 색을 잇나?
```

**정답**:
1. `--p: #156BFF` (밝은 블루), `--a: #00C8E5` (시안)
2. njob = `#003CDC` + sky `#5BC2E7` + bg `#E6EDFF`
   rebuild = `#FF6A00` + sky `#FF9A4D` + bg `#FFEDDB`
3. `#156BFF` → `#00C8E5` (블루에서 시안으로 135deg)

3개 다 정답 → ✅ Claude Code가 디자인 시스템 정확히 인지.
