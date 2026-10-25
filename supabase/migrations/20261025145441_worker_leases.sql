-- Separate server privileges. Login credentials are provisioned outside Git.
create role gtm_api nologin nosuperuser nobypassrls;
create role gtm_worker nologin nosuperuser nobypassrls;
grant gtm_api, gtm_worker to postgres;
grant usage on schema gtm to gtm_api, gtm_worker;
grant select, insert on gtm.projects to gtm_api;
create policy projects_api_read on gtm.projects for select to gtm_api
    using (owner_id = (select nullif(current_setting('gtm.owner_id',true),'')::uuid));
create policy projects_api_create on gtm.projects for insert to gtm_api
    with check (owner_id = (select nullif(current_setting('gtm.owner_id',true),'')::uuid));

alter table gtm.jobs add column lease_token uuid;
alter table gtm.jobs add column lease_expires_at timestamptz;
alter table gtm.jobs add constraint jobs_lease_state check (
    (state = 'running' and lease_token is not null and lease_expires_at is not null)
    or (state <> 'running' and lease_token is null and lease_expires_at is null)
);
grant select, update on gtm.jobs to gtm_worker;
create policy jobs_worker_read on gtm.jobs for select to gtm_worker using (true);
create policy jobs_worker_update on gtm.jobs for update to gtm_worker
    using (true) with check (true);

create function gtm.claim_job(p_task_types text[], p_lease_seconds integer default 60)
returns setof gtm.jobs language plpgsql security invoker set search_path = '' as $$
begin
    if p_lease_seconds < 15 or p_lease_seconds > 300 or p_lease_seconds is null then
        raise exception 'invalid_lease_duration';
    end if;
    return query
    update gtm.jobs j set state = 'running', attempt = j.attempt + 1,
        heartbeat_at = clock_timestamp(), updated_at = clock_timestamp(), error_code = null,
        lease_token = gen_random_uuid(),
        lease_expires_at = clock_timestamp() + make_interval(secs => p_lease_seconds)
    where j.id = (
        select q.id from gtm.jobs q where q.state = 'queued'
            and q.attempt < q.max_attempts and q.available_at <= clock_timestamp()
            and q.task_type = any(p_task_types)
        order by q.available_at, q.created_at, q.id limit 1 for update skip locked
    ) returning j.*;
end;
$$;

create function gtm.heartbeat_job(p_id uuid, p_token uuid, p_lease_seconds integer default 60)
returns boolean language plpgsql security invoker set search_path = '' as $$
declare affected integer;
begin
    if p_lease_seconds < 15 or p_lease_seconds > 300 or p_lease_seconds is null then
        raise exception 'invalid_lease_duration';
    end if;
    update gtm.jobs set heartbeat_at = clock_timestamp(), updated_at = clock_timestamp(),
        lease_expires_at = clock_timestamp() + make_interval(secs => p_lease_seconds)
    where id = p_id and state = 'running' and lease_token = p_token
        and lease_expires_at > clock_timestamp();
    get diagnostics affected = row_count;
    return affected = 1;
end;
$$;

create function gtm.finish_job(p_id uuid, p_token uuid, p_state text, p_error text default null)
returns boolean language plpgsql security invoker set search_path = '' as $$
declare affected integer;
begin
    if p_state is null or p_state not in ('completed','partial','failed','queued')
        or (p_error is not null and p_error not in ('handler_failed','retry_safe','outcome_unknown'))
        or (p_state = 'queued' and p_error is distinct from 'retry_safe') then
        raise exception 'invalid_job_result';
    end if;
    update gtm.jobs set state = case
            when p_state = 'queued' and attempt >= max_attempts then 'failed' else p_state end,
        error_code = p_error, lease_token = null, lease_expires_at = null,
        updated_at = clock_timestamp(), available_at = clock_timestamp() + interval '30 seconds'
    where id = p_id and state = 'running' and lease_token = p_token
        and lease_expires_at > clock_timestamp();
    get diagnostics affected = row_count;
    return affected = 1;
end;
$$;

-- Expired work may already have caused a charge: never requeue automatically.
create function gtm.expire_jobs() returns integer
language plpgsql security invoker set search_path = '' as $$
declare affected integer;
begin
    update gtm.jobs set state = 'failed', error_code = 'outcome_unknown',
        lease_token = null, lease_expires_at = null, updated_at = clock_timestamp()
    where state = 'running' and lease_expires_at <= clock_timestamp();
    get diagnostics affected = row_count;
    return affected;
end;
$$;
revoke all on function gtm.claim_job(text[],integer),
    gtm.heartbeat_job(uuid,uuid,integer), gtm.finish_job(uuid,uuid,text,text), gtm.expire_jobs()
    from public, anon, authenticated, service_role, gtm_api;
grant execute on function gtm.claim_job(text[],integer),
    gtm.heartbeat_job(uuid,uuid,integer), gtm.finish_job(uuid,uuid,text,text), gtm.expire_jobs()
    to gtm_worker;
