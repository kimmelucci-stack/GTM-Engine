-- One budget groups all module runs belonging to the same full GTM execution.
create table gtm.budgets (
    id uuid primary key default gen_random_uuid(),
    project_id uuid not null references gtm.projects(id),
    cap_usd numeric not null check (cap_usd > 0 and cap_usd <= 15),
    max_requests integer not null default 100 check (max_requests between 1 and 10000),
    halted boolean not null default false,
    unmeasured text[] not null default '{}',
    created_at timestamptz not null default now(),
    unique (id, project_id)
);
create index budgets_project_idx on gtm.budgets(project_id);

alter table gtm.runs add column budget_id uuid;
alter table gtm.runs add constraint runs_budget_project_fk
    foreign key (budget_id,project_id) references gtm.budgets(id,project_id);
alter table gtm.runs add constraint runs_budget_id_unique unique (budget_id,id);
create index runs_budget_project_idx on gtm.runs(budget_id,project_id);

create table gtm.cost_events (
    budget_id uuid not null references gtm.budgets(id),
    event_id text not null check (length(trim(event_id)) between 1 and 128),
    run_id uuid not null,
    provider text not null check (length(trim(provider)) between 1 and 80),
    endpoint text not null check (length(trim(endpoint)) between 1 and 512),
    component text not null check (component in ('data','ai','execution','allocated_fixed')),
    ceiling_usd numeric not null check (ceiling_usd >= 0 and ceiling_usd <= 15),
    actual_usd numeric check (actual_usd >= 0 and actual_usd not in ('NaN','Infinity','-Infinity')),
    status text not null check (status in ('reserved','uncertain','settled','overrun')),
    created_at timestamptz not null default now(),
    settled_at timestamptz,
    primary key (budget_id,event_id),
    foreign key (budget_id,run_id) references gtm.runs(budget_id,id),
    check ((actual_usd is null and status in ('reserved','uncertain') and settled_at is null)
        or (actual_usd is not null and status in ('settled','overrun') and settled_at is not null))
);
create index cost_events_run_idx on gtm.cost_events(budget_id,run_id);

alter table gtm.budgets enable row level security;
alter table gtm.budgets force row level security;
alter table gtm.cost_events enable row level security;
alter table gtm.cost_events force row level security;
revoke all on gtm.budgets,gtm.cost_events from public,anon,authenticated,service_role;

grant select,insert on gtm.budgets to gtm_api;
create policy budgets_api_read on gtm.budgets for select to gtm_api using (
    exists (select 1 from gtm.projects p where p.id = budgets.project_id)
);
create policy budgets_api_create on gtm.budgets for insert to gtm_api with check (
    not halted and unmeasured = '{}'::text[]
    and exists (select 1 from gtm.projects p where p.id = budgets.project_id)
);

grant select on gtm.budgets,gtm.cost_events to gtm_worker;
grant update(halted,unmeasured) on gtm.budgets to gtm_worker;
grant insert on gtm.cost_events to gtm_worker;
grant update(actual_usd,status,settled_at) on gtm.cost_events to gtm_worker;
create policy budgets_worker_read on gtm.budgets for select to gtm_worker using (true);
create policy budgets_worker_update on gtm.budgets for update to gtm_worker using (true) with check (true);
create policy cost_events_worker_read on gtm.cost_events for select to gtm_worker using (true);
create policy cost_events_worker_insert on gtm.cost_events for insert to gtm_worker with check (true);
create policy cost_events_worker_update on gtm.cost_events for update to gtm_worker using (true) with check (true);

comment on table gtm.budgets is 'Full GTM execution budget shared by module runs. Mutations serialize by row lock.';
comment on column gtm.runs.budget_id is 'Required by cost reservation; legacy unbudgeted runs cannot incur budgeted charges.';
comment on table gtm.cost_events is 'USD reservations and actuals, never provider response bodies or credentials.';
