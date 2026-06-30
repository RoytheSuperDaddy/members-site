# DB Schema Reference

Supabase Project: `vvgghtpntxffysxijkxk`

## events

| Column | Type | Required | Notes |
|--------|------|----------|-------|
| id | BIGINT (PK) | auto | 자동 증가 |
| event_date | DATE | ✓ | 일정 날짜 |
| day_num | INT | auto | event_date에서 추출 |
| month_label | VARCHAR(10) | auto | JAN~DEC |
| title | VARCHAR(200) | ✓ | 업무명 |
| description | TEXT | - | 상세 |
| tag | VARCHAR(20) | ✓ | t-imp / t-reg / t-ddl |
| tag_text | VARCHAR(20) | auto | 중요 / 정기 / 마감 (tag 매핑) |
| category | VARCHAR(30) | ✓ | exam/report/reward/education/meeting/sign/general |
| actions | JSONB | - | 액션 항목 배열 |

## notices

| Column | Type | Required | Notes |
|--------|------|----------|-------|
| id | BIGINT (PK) | auto | |
| icon | VARCHAR(10) | - | default: 📢 |
| icon_class | VARCHAR(20) | - | i-blue/i-orange/i-green/i-purple/i-pink |
| title | VARCHAR(200) | ✓ | |
| author | VARCHAR(50) | - | default: 멤버스 운영팀 |
| body | TEXT | ✓ | markdown 허용 |

## guides

| Column | Type | Required | Notes |
|--------|------|----------|-------|
| id | BIGINT (PK) | auto | |
| main_category | VARCHAR(20) | ✓ | njob/rebuild/faq |
| category | VARCHAR(20) | ✓ | 서브카테고리 |
| icon | VARCHAR(10) | - | main_category 기반 자동 |
| icon_class | VARCHAR(20) | - | main_category 기반 자동 |
| title | VARCHAR(200) | ✓ | |
| description | TEXT | ✓ | |
| badge | VARCHAR(20) | - | b-new (default) |
| badge_text | VARCHAR(20) | - | NEW (default) |
| steps | JSONB | ✓ | 단계 배열 |
| note | TEXT | - | 핵심 포인트 |
| copyable_text | TEXT | - | 복붙용 카톡 문구 |

## 자동 매핑 룰

### events.tag → tag_text

| tag | tag_text |
|-----|---------|
| t-imp | 중요 |
| t-reg | 정기 |
| t-ddl | 마감 |

### events.event_date → day_num, month_label

- day_num: event_date의 day 부분 (DD)
- month_label: ['JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC']

### guides.main_category → icon, icon_class

| main_category | icon | icon_class |
|---------------|------|-----------|
| njob | 📋 | i-blue |
| rebuild | 🔄 | i-orange |
| faq | ❓ | i-green |

## 카테고리 enum 값

### events.category

| 값 | 의미 |
|----|------|
| exam | 시험 |
| report | 보고 |
| reward | 시상/리워드 |
| education | 교육 |
| meeting | 회의 |
| sign | 서명/등록 |
| general | 일반 |

### guides.main_category 서브카테고리

**njob**: 유입 / 학습 / 시험 / 코드등록 / 가동

**rebuild**: 이관 / 친숙 / 가동 / 수수료전환 / 계속분관리

**faq**: 서브 없음
