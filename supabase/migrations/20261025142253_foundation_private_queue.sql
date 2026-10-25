-- Server-only foundation. No browser grants or permissive RLS policies.
create schema gtm;
revoke all on schema gtm from public, anon, authenticated, service_role;
alter default privileges in schema gtm revoke all on tables from public, anon, authenticated, service_role;
alter default privileges in schema gtm revoke execute on functions from public, anon, authenticated, service_role;
alter default privileges in schema gtm revoke all on sequences from public, anon, authenticated, service_role;

create table gtm.projects (
    id uuid primary key default gen_random_uuid(),
    owner_id uuid not null references auth.users(id),
    title text not null check (length(trim(title)) between 1 and 200),
    offer_brief jsonb not null check (jsonb_typeof(offer_brief) = 'object'),
    product_in_development boolean not null,
    geo jsonb not null check (jsonb_typeof(geo) = 'object'),
    locale text not null default 'it-IT',
    created_at timestamptz not null default now()
);
create index projects_owner_idx on gtm.projects(owner_id);

create table gtm.runs (
    id uuid primary key default gen_random_uuid(),
    project_id uuid not null references gtm.projects(id),
    module_no smallint not null check (module_no between 1 and 7),
    mode text not null check (length(trim(mode)) > 0),
    status text not null default 'queued'
        check (status in ('queued', 'running', 'completed', 'partial', 'failed', 'cancelled')),
    cost_cap numeric(12,6) not null check (cost_cap > 0 and cost_cap <= 15),
    created_at timestamptz not null default now(),
    started_at timestamptz,
    completed_at timestamptz,
    check (completed_at is null or (started_at is not null and completed_at >= started_at))
);
create index runs_project_idx on gtm.runs(project_id, created_at);

create table gtm.jobs (
    id uuid primary key default gen_random_uuid(),
    run_id uuid not null references gtm.runs(id),
    task_type text not null check (length(trim(task_type)) > 0),
    state text not null default 'queued'
        check (state in ('queued', 'running', 'completed', 'partial', 'failed', 'cancelled')),
    attempt integer not null default 0 check (attempt >= 0),
    max_attempts integer not null default 3 check (max_attempts between 1 and 5),
    available_at timestamptz not null default now(),
    heartbeat_at timestamptz,
    error_code text,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    check (attempt <= max_attempts)
);
create index jobs_run_idx on gtm.jobs(run_id);
create index jobs_pending_idx on gtm.jobs(available_at, created_at) where state = 'queued';
create index jobs_heartbeat_idx on gtm.jobs(heartbeat_at) where state = 'running';

alter table gtm.projects enable row level security;
alter table gtm.projects force row level security;
alter table gtm.runs enable row level security;
alter table gtm.runs force row level security;
alter table gtm.jobs enable row level security;
alter table gtm.jobs force row level security;
revoke all on all tables in schema gtm from public, anon, authenticated, service_role;

comment on schema gtm is 'Internal persistence. No client access. Runtime role and owner authorization pending.';
comment on column gtm.runs.cost_cap is 'USD module ceiling; not a cross-provider ledger or proof of full-GTM affordability.';
comment on column gtm.jobs.error_code is 'Sanitized stable code only. Never raw provider errors or credentials.';
