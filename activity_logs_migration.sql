-- 이용 로그 테이블 (접속 · 입과 안내문 생성 추적)
-- Supabase Dashboard → SQL Editor 에 붙여넣어 실행하세요.
-- 프로젝트: vvgghtpntxffysxijkxk

create table if not exists public.activity_logs (
  id         bigint generated always as identity primary key,
  user_id    text not null,
  action     text not null,               -- 'login' | 'welcome_guide'
  meta       jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create index if not exists idx_activity_logs_created      on public.activity_logs(created_at);
create index if not exists idx_activity_logs_user_created on public.activity_logs(user_id, created_at);

-- 앱은 anon 키로 직접 접근하므로 anon 에 insert/select 권한 부여 (기존 테이블과 동일 모델)
alter table public.activity_logs enable row level security;

drop policy if exists "activity_logs anon insert" on public.activity_logs;
create policy "activity_logs anon insert" on public.activity_logs
  for insert to anon, authenticated with check (true);

drop policy if exists "activity_logs anon select" on public.activity_logs;
create policy "activity_logs anon select" on public.activity_logs
  for select to anon, authenticated using (true);

grant insert, select on public.activity_logs to anon, authenticated;
