-- Explicit foundation operations only. This does not enable billable module workflows.
alter table gtm.runs add column request_id uuid;
alter table gtm.runs add constraint runs_request_unique unique(project_id,request_id);
create unique index jobs_foundation_once on gtm.jobs(run_id)
    where task_type in ('catalog.validate','catalog.archive');

grant insert on gtm.runs,gtm.jobs to gtm_api;
grant select on gtm.jobs to gtm_api;
create policy runs_api_create on gtm.runs for insert to gtm_api with check (
    project_id in (select id from gtm.projects)
    and request_id is not null and module_no=1
    and mode in ('foundation:catalog.validate','foundation:catalog.archive')
    and status='queued' and started_at is null and completed_at is null
    and budget_id in (select id from gtm.budgets where project_id=runs.project_id
        and cap_usd=runs.cost_cap and not halted)
);
create policy jobs_api_read on gtm.jobs for select to gtm_api
    using (run_id in (select id from gtm.runs));
create policy jobs_api_create on gtm.jobs for insert to gtm_api with check (
    state='queued' and attempt=0 and error_code is null and heartbeat_at is null
    and lease_token is null and lease_expires_at is null
    and ((task_type='catalog.validate' and max_attempts=3)
         or (task_type='catalog.archive' and max_attempts=1))
    and run_id in (select id from gtm.runs where mode='foundation:' || jobs.task_type
        and request_id is not null and status='queued')
);

grant update(status,started_at,completed_at) on gtm.runs to gtm_worker;
create policy runs_worker_update on gtm.runs for update to gtm_worker
    using (true) with check (true);

-- Invoker trigger runs only on worker state transitions, never on API INSERT.
-- Lock the parent before reading all children so parallel finishes serialize correctly.
create function gtm.sync_run_state() returns trigger language plpgsql
security invoker set search_path='' as $$
declare
    n integer; pending integer; active integer; done integer; broken integer;
    limited integer; stopped integer; begun boolean; next_state text;
begin
    perform id from gtm.runs where id=new.run_id for update;
    select count(*),count(*) filter(where state='queued'),count(*) filter(where state='running'),
        count(*) filter(where state='completed'),count(*) filter(where state='failed'),
        count(*) filter(where state='partial'),count(*) filter(where state='cancelled'),
        coalesce(bool_or(attempt>0),false)
    into n,pending,active,done,broken,limited,stopped,begun
    from gtm.jobs where run_id=new.run_id;
    next_state := case
        when active>0 then 'running' when pending>0 or n=0 then 'queued'
        when done=n then 'completed' when stopped=n then 'cancelled'
        when limited>0 or (done>0 and broken+stopped>0) then 'partial'
        when broken>0 then 'failed' else 'partial' end;
    update gtm.runs set status=next_state,
        started_at=case when begun then coalesce(started_at,clock_timestamp()) else started_at end,
        completed_at=case when next_state in ('completed','partial','failed','cancelled')
            then coalesce(completed_at,clock_timestamp()) else null end
    where id=new.run_id;
    return new;
end;
$$;
revoke all on function gtm.sync_run_state() from public,anon,authenticated,service_role,gtm_api;
grant execute on function gtm.sync_run_state() to gtm_worker;
create trigger jobs_sync_run after update of state,attempt on gtm.jobs
    for each row execute function gtm.sync_run_state();
