-- Private cross-device study state for Supabase Auth users.
-- Run in this project's SQL Editor. Existing public.user_progress is preserved.
begin;
create table if not exists public.study_progress_items (
    user_id uuid not null references auth.users(id) on delete cascade,
    item_key text not null check (char_length(item_key) <= 200),
    value jsonb not null,
    updated_at timestamptz not null default now(),
    primary key (user_id, item_key)
);
alter table public.study_progress_items enable row level security;
grant select, insert, update on table public.study_progress_items to authenticated;
create policy study_progress_select on public.study_progress_items
    for select to authenticated using ((select auth.uid()) = user_id);
create policy study_progress_insert on public.study_progress_items
    for insert to authenticated with check ((select auth.uid()) = user_id);
create policy study_progress_update on public.study_progress_items
    for update to authenticated using ((select auth.uid()) = user_id)
    with check ((select auth.uid()) = user_id);
commit;
