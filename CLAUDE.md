# N잡크루 멤버스 허브 - Claude Code Project Memory

> 매 세션 자동 로드. 200줄 이내 유지. 실제 `index.html` 토큰 기반.

## 프로젝트 개요

- **서비스**: 삼성화재 멤버스센터 운영 허브 (멤버스팀장 전용)
- **파일**: 단일 HTML (`index.html`), Vanilla JS, 인라인 CSS
- **DB**: Supabase (`vvgghtpntxffysxijkxk`)
- **호스팅**: Vercel auto-deploy → `sfmi.members-center.co.kr`
- **사용자**: 30~60대 보험 영업 간부 (고연령 가독성 우선)
- **테이블**: members / guides / events / notices
- **이중 브랜드**: N잡크루 (영입) + 리빌딩 (수수료 전환) 사업부 분리

## 디자인 철학

**Vibrant Brand + Dual Sub-brand 시스템**
- 메인 멤버스센터: Blue→Cyan 그라데이션 (`--gr-hero`)
- 서브브랜드 분리: N잡크루(`--njob` #003CDC) / 리빌딩(`--rebuild` #FF6A00)
- 핵심 특징: gradient hero card + radial overlay + 좌측 카테고리 액센트 바
- 고연령 친화: 본문 14-15px, 명확한 위계

## 디자인 토큰 (실제 :root - 그대로 사용)

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
  --g50:#F4F6FA; --g100:#E5E8EF; --g200:#C9D0DC; --g400:#8A92A3;
  --g600:#5A6478; --g800:#1A2238; --g900:#0A1433;

  /* Semantic */
  --ok:#00A878; --err:#E53E3E; --warn:#F59E0B;

  /* Geometry & Shadow */
  --r:14px; --rs:8px;
  --sh:0 2px 16px rgba(10,20,51,.06);
  --sh-lg:0 8px 32px rgba(10,20,51,.1);

  /* Font */
  --f:'Noto Sans KR', sans-serif;
}
```

## 폰트 시스템

```css
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700;900&display=swap');
@font-face{font-family:'SamsungGL';src:url('fonts/SamsungGothicLong-Regular.ttf') format('truetype');font-weight:400}
@font-face{font-family:'SamsungGL';src:url('fonts/SamsungGothicLong-UltraLight.ttf') format('truetype');font-weight:200}
```

- **본문**: Noto Sans KR (300/400/500/700/900)
- **보조**: SamsungGL (200, 400) — 로컬 `fonts/` 폴더 필요
- ❌ Pretendard, Inter, Roboto 사용 금지

## Typography 규칙

- **Hero/Page Title**: 22px / 900 / letter-spacing -0.5px
- **Section Title**: 14-15px / 700-900
- **Body**: 14-15px / 400-500 (최소값, 13px 이하 금지)
- **Card Title (.tcn, .nit)**: 14px / 700
- **Meta (.tcm, .nim)**: 11-12px / var(--g400)
- **Tag/Badge**: 10-11px / 700
- **KPI/Stat (.sv)**: 24px / 900

## Component Patterns

- **Card (.tc, .gc, .ni)**: `bg:w + 1.5px solid g100 + r-lg + sh`, hover `translateY(-2px) + sh-lg`
- **Hero Card (.tg)**: `--gr-hero + 2 radial overlay (white + coral)`, padding 24px 26px, radius 16px
- **Auth Screen (.aw)**: 어두운 deep gradient (`#06091B → #0D2D6E`) + radial overlay (cyan/coral)
- **Header**: `--gr-hero-deep` gradient
- **Sidebar (.desk-side)**: 220px, active state `bg:#E6EFFF + color:p + 우측 3px solid p border`
- **Calendar Header (.cal-hdr)**: solid `--p`
- **Modal (.md)**: 18px radius, backdrop blur 3px
- **Toast**: `#1A1F35` dark bg

## 카테고리별 좌측 액센트 바 (.gc::before)

가이드 카드에 좌측 4px 액센트로 카테고리 시각화:
- `.gc.is-njob::before` → `--njob` (#003CDC, 진파랑)
- `.gc.is-rebuild::before` → `--rebuild` (#FF6A00, 오렌지)
- `.gc.is-faq::before` → `--ok` (#00A878, 그린)

## 아이콘 박스 컬러 시스템

라운드 박스 + 이모지 (`.gic`, `.nic`, `.tci`):
- `.i-blue` #E6EFFF / `.i-orange` #FFE8E0 / `.i-cyan` #DEF7FB
- `.i-green` #E8F8F4 / `.i-purple` #F0EBFF / `.i-pink` #FFF0F6

## 뱃지 시스템 (.gbg)

- `.b-new` #FFE8E0/#E5563A (NEW)
- `.b-up` #DEF7FB/#007FA0 (업데이트)
- `.b-def` g100/g400 (기본)
- `.b-njob` #E0E8FF/#003CDC
- `.b-rebuild` #FFE8D6/#FF6A00

## 일정 태그 (.tct, .evtg)

- `.t-imp` #FFE8E8/#D63031 (중요)
- `.t-reg` #E8F4FF/#0063CC (정기)
- `.t-ddl` #FFF3EA/#E67E22 (마감)
- `.t-bday` #FFF0F6/#D63071 (생일)

## 어셋 시스템 (assets/ 폴더, 18종)

| 어셋 | 용도 |
|---|---|
| `members-horizontal.png` | 로그인/헤더/사이드바 메인 로고 (실사용) |
| `members-stack.png`, `members-symbol.png` | 변형 로고 (향후 확장) |
| `njobcrew-ci.png`, `njobcrew-symbol-t.png` | N잡크루 페이지용 |
| `rebuilding-horizontal.png`, `rebuilding-symbol.png` | 리빌딩 페이지용 |
| `samsungfire-ko.png` | 삼성화재 모회사 로고 |
| `m-h/s/sy.png`, `r-h/s/sy.png` | 축약형 (작은 영역용) |

**카드 배경 흰색 필수**: 로고 이미지 표시 시 `background:rgba(255,255,255,.96)` + padding으로 가독성 확보.

## Motion 규칙

- transition: `.15s` 표준, `.2s` cards
- Auth 등장: `translateY(20px) → 0`, `.5s ease`
- 모달 등장: `scale(.96) → 1`, `.25s ease`
- 챗 패널: `translateY(20px) → 0`, `.25s ease`
- Hover lift: cards `translateY(-2px) + sh-lg`

## 작업 규칙

1. **전체 파일 재생성 금지** → `str_replace` 단위 부분 수정
2. **토큰 변경은 `:root`만** (컴포넌트 일괄 반영)
3. **DB 작업은 Supabase MCP로 직접 SQL 실행**
4. **명명**: 기존 짧은 약어 유지 (`hl`, `tc`, `gc`, `evi`, `mnb` 등)
5. **응답**: 진단(표) → 패치(코드) → 다음 단계(체크리스트)
6. **이미지 사용 시**: `assets/` 폴더 경로, 흰 배경 padding 적용
7. **인증**: SHA-256(`8072d521...` = `n1234`), 관리자 ID `10000001~05`

## DB 핵심 컬럼

- **members**: user_id(8자리), password_hash, name, phone, role, status(init/active/locked), org_*, birthday, birthday_type
- **guides**: main_category(njob/rebuild/faq), category, title, description, steps(JSONB), note, copyable_text, badge
- **events**: event_date, day_num, month_label, title, tag(t-imp/t-reg/t-ddl), category, actions(JSONB)
- **notices**: icon, icon_class, title, author, body

## 카테고리 구조

- **njob**: 유입 / 학습 / 시험 / 코드등록 / 가동 (5단계)
- **rebuild**: 이관 / 친숙 / 가동 / 수수료전환 / 계속분관리 (5단계)
- **faq**: 서브 없음

## 출력 형식

- Top-down: 결론 → 본문 → 다음 단계
- Markdown 적극 활용 (표/코드/체크리스트)
- 한국어 본문 + 기술 용어는 영어 그대로
- 금지: "도움이 되셨길~", "일반적으로~", 사과/감탄사
- 짧되 정보 밀도 높게

## 워크플로우

작업 후 순서:
1. 변경 사항 요약 (표)
2. `git diff` 결과
3. 사용자 승인 → `git add`
4. Conventional Commits (feat/fix/refactor/style/docs)
5. push 전 재승인
6. Vercel Preview URL 안내

## 금지 사항

- ❌ Pretendard, Inter, Roboto 폰트
- ❌ 보라/마젠타 메인 컬러
- ❌ 13px 이하 본문
- ❌ 카드 1개에 emoji 2개 이상
- ❌ N잡 컬러를 리빌딩 페이지에, 또는 그 반대로 사용
- ❌ 그라데이션 직접 작성 (`--gr-*` 변수만 사용)
