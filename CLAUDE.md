# N잡크루 멤버스 허브 - Claude Code Project Memory

> 매 세션 자동 로드. `index.html`의 실제 토큰 기반. 200줄 이내 유지.

## 프로젝트 개요

- **서비스**: 삼성화재 멤버스센터 운영 허브 (팀장/센터장/총무 전용)
- **파일**: 단일 HTML (`index.html`), Vanilla JS, 인라인 CSS, Supabase JS SDK
- **DB**: Supabase (project `vvgghtpntxffysxijkxk`)
- **호스팅**: Vercel auto-deploy → `sfmi.members-center.co.kr`
- **사용자**: 30~60대 보험 영업 간부 (고연령 가독성 우선)
- **이중 브랜드**: N잡크루 + 리빌딩 (서브브랜드 색상 분리 시스템)

## 디자인 철학

**Brand-Forward + Vibrant Hero (이중 브랜드 시스템)**
- 메인: 밝은 블루(`#156BFF`) + 시안(`#00C8E5`) 그라데이션 톤
- N잡크루(딥블루) ↔ 리빌딩(오렌지) 사업부 구분
- 코랄 액센트(`#FF7A59`)는 hero 보조 hot spot
- 고연령 친화: 본문 14-15px, 명확한 위계

## 디자인 토큰 (그대로 `:root`에 사용)

```css
:root{
  /* 멤버스센터 Primary */
  --p:#156BFF; --pd:#0A1433; --pl:#4A8DFF; --pt:#0D4FCC;
  --a:#00C8E5; --al:#5DDCEC; --coral:#FF7A59;

  /* 그라디언트 4종 */
  --gr-hero:linear-gradient(135deg,#156BFF 0%,#00C8E5 100%);
  --gr-hero-deep:linear-gradient(135deg,#0A1433 0%,#0D4FCC 50%,#156BFF 100%);
  --gr-soft:linear-gradient(135deg,#E6EFFF 0%,#DEF7FB 100%);
  --gr-warm:linear-gradient(135deg,#FF7A59 0%,#FFB084 100%);

  /* 서브브랜드 */
  --njob:#003CDC; --njob-sky:#5BC2E7; --njob-bg:#E6EDFF;
  --rebuild:#FF6A00; --rebuild-sky:#FF9A4D; --rebuild-bg:#FFEDDB;

  /* 그레이/배경 */
  --bg:#F4F6FB; --w:#fff;
  --g50:#F4F6FA; --g100:#E5E8EF; --g200:#C9D0DC;
  --g400:#8A92A3; --g600:#5A6478; --g800:#1A2238; --g900:#0A1433;

  /* Semantic */
  --ok:#00A878; --err:#E53E3E; --warn:#F59E0B;

  /* Shadow + 기하 */
  --r:14px; --rs:8px;
  --sh:0 2px 16px rgba(10,20,51,.06);
  --sh-lg:0 8px 32px rgba(10,20,51,.1);

  --f:'Noto Sans KR',sans-serif;
}
```

**폰트 (head에 반드시 포함)**:
```html
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700;900&display=swap');
@font-face{font-family:'SamsungGL';src:url('fonts/SamsungGothicLong-Regular.ttf') format('truetype');font-weight:400}
@font-face{font-family:'SamsungGL';src:url('fonts/SamsungGothicLong-UltraLight.ttf') format('truetype');font-weight:200}
```

## Typography 규칙

- **Hero**: 22px / 900 / -0.4em (페이지 상단 카드 타이틀)
- **Page Title**: 22px / 900 / -0.5em (`.pt`)
- **Section Title**: 14px / 700 (`.tst`)
- **Card Title**: 14px / 700 (`.tcn`, `.gti`)
- **Body**: 15px / 400-500 (`.body 기본`)
- **Meta**: 12-13px / 500-600 (`.tcm`, `.pd`)
- **Tag/Label**: 10-11px / 700, 라운드 박스
- **금지**: 13.5px 이하 본문, light(300) 이하 weight

## Component Patterns

### Hero Card (오늘 인사 카드)
- `background:var(--gr-hero)` + 흰색 텍스트
- **2종 radial overlay** (필수): white(top-right) + coral(bottom)
- `box-shadow:0 8px 24px rgba(21,107,255,.18)`
- 텍스트는 `position:relative; z-index:2`

### Header (sticky)
- `background:var(--gr-hero-deep)` (3-stop 깊은 그라데이션)
- 56px 높이, white 텍스트
- 로고 이미지: `assets/members-horizontal.png` (height 32px, white padding bg)

### Sidebar (220px)
- white bg + `--g100` 우측 보더
- nav-section: label(10px UPPERCASE g400) + ds-btn
- **active state**: bg `#E6EFFF` + color `var(--p)` + 우측 3px brand border

### Card 표준 (`.tc`, `.gc`, `.fc`)
- `bg:white + border:1.5px var(--g100) + sh + r 14px`
- hover: `translateY(-2px) + 0 6px 20px rgba(0,62,138,.12)`

### Guide Card 좌측 컬러 바 (`.gc::before`)
- `.is-njob` → `var(--njob)` (딥블루 #003CDC)
- `.is-rebuild` → `var(--rebuild)` (오렌지 #FF6A00)
- `.is-faq` → `var(--ok)` (그린)
- 4px 폭, 카드 좌측 100% 높이

### Icon Box (6종 컬러)
- `.i-blue:#E6EFFF` / `.i-orange:#FFE8E0` / `.i-cyan:#DEF7FB`
- `.i-green:#E8F8F4` / `.i-purple:#F0EBFF` / `.i-pink:#FFF0F6`

### Badge (`.gbg`, 가이드 상단 우측)
- `b-new:#FFE8E0/#E5563A` (NEW)
- `b-up:#DEF7FB/#007FA0` (업데이트)
- `b-def:var(--g100)/var(--g400)` (기본)
- `b-njob:#E0E8FF/#003CDC` / `b-rebuild:#FFE8D6/#FF6A00`

### Tag (`.t-*`, 일정/카드 우측)
- `t-imp:#FFE8E8/#D63031` (중요)
- `t-reg:#E8F4FF/#0063CC` (정기)
- `t-ddl:#FFF3EA/#E67E22` (마감)
- `t-bday:#FFF0F6/#D63071` (생일)

### Calendar
- header solid `var(--p)` bg + white 텍스트
- today cell: `#E6EFFF` bg, day num을 brand 원형 안에
- event chip: 사용 tag별 컬러

### Form
- input/textarea: `bg:var(--g50) + border:1.5px var(--g200)`
- focus: `border:var(--p) + bg:white`
- label: 11px 700 g600

### Modal
- backdrop: `rgba(0,0,0,.45) + blur(3px)`
- container: 18px radius, `shadow:0 16px 48px rgba(0,0,0,.2)`
- animation: scale(.96 → 1) + opacity 0.25s

## Motion 규칙

- transition: `.15s` (color/bg/transform), `.2s` (shadow/카드 lift)
- 카드 hover: `translateY(-2px)` + shadow 한 단계 up
- 모달: scale 0.96 → 1, fade in
- 금지: bouncing, parallax, slide-in 1초 이상

## 어셋 사용 규칙

- 로고는 **항상 `assets/members-horizontal.png`** 사용 (현재 5곳에서 참조)
- 추가 어셋 폴더에 보관 (미사용이지만 향후 확장 대비):
  - `members-symbol.png`, `members-stack.png` (스택형 변형)
  - `rebuilding-horizontal.png`, `rebuilding-symbol.png` (리빌딩 사업부)
  - `njobcrew-ci.png`, `samsungfire-ko.png` (상위 CI)
- 흰색 배경 카드 위에 로고 배치 시: `background:rgba(255,255,255,.96)` + padding으로 처리

## 금지 사항

- ❌ 다른 폰트 우선 사용 (Noto Sans KR + SamsungGL 강제)
- ❌ 보라/핑크 hero 그라데이션 (브랜드 톤 이탈)
- ❌ `border-radius: 24px+` (모달 18px만 예외)
- ❌ 13.5px 이하 본문 텍스트
- ❌ 단색 hero 카드 (그라데이션 + radial overlay 필수)
- ❌ N잡크루 / 리빌딩 색상 혼용 (각 영역에 맞는 서브브랜드 사용)
- ❌ 새 색상 추가 (기존 토큰에서 조합)

## 작업 규칙

1. **전체 파일 재생성 금지** → `str_replace` 단위 부분 수정
2. **토큰 변경은 `:root` 변수만 수정** (컴포넌트 일괄 변경)
3. **DB 작업은 Supabase MCP로 직접 SQL 실행**
4. **명명**: 기존 짧은 변수명 유지 (`hl`, `tc`, `evi` 등 kebab-case/약어)
5. **응답 구조**: 진단(표) → 패치(코드) → 다음 단계(체크리스트)
6. **인증 정보**: 초기PW `n1234` (SHA-256: `8072d521...`), 관리자 ID `10000001~05`

## DB 테이블 핵심

| 테이블 | 핵심 컬럼 |
|---|---|
| **members** | user_id(8자리), password_hash, name, phone, role, status(init/active/locked), org_division, org_region, org_center, birthday(MM-DD), birthday_type |
| **guides** | main_category(njob/rebuild/faq), category, title, description, steps(JSONB), note, copyable_text, badge |
| **events** | event_date, title, description, tag(t-imp/t-reg/t-ddl), category, actions(JSONB) |
| **notices** | icon, icon_class, title, author, body |

## 가이드 카테고리

- **njob**: 유입단계 / 학습단계 / 시험단계 / 코드등록단계 / 가동단계
- **rebuild**: 이관 / 친숙 / 가동 / 수수료전환 / 계속분관리
- **faq**: 서브 카테고리 없음

## 출력 형식

- Top-down: 결론 → 본문 → 다음 단계
- Markdown 적극 활용 (표 / 코드블록 / 체크리스트)
- 한국어 본문 + 기술 용어는 영어 그대로
- 금지 멘트: "도움이 되셨길~", "일반적으로~", "AI로서 한계~", 사과/감탄사
- 짧되 정보 밀도 높게

## 작업 워크플로우

1. 변경 사항 요약(표)
2. `git diff` 결과 표시
3. 사용자 승인 시 `git add`
4. commit message: Conventional Commits (feat/fix/refactor/style/docs)
5. push 전 재승인
6. Vercel Preview URL 안내
