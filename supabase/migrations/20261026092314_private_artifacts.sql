-- Application metadata only. Storage objects are managed exclusively through its HTTP API.
create table gtm.artifacts (
    id uuid primary key,
    run_id uuid not null references gtm.runs(id),
    kind text not null check (kind in ('raw','normalized','derived','deliverable')),
    bucket text not null default 'gtm-evidence' check (bucket = 'gtm-evidence'),
    storage_key text not null unique,
    sha256 text not null check (sha256 ~ '^[0-9a-f]{64}$'),
    byte_size integer not null check (byte_size between 1 and 6291456),
    content_type text not null check (content_type in ('application/json','text/plain',
        'text/html','image/png','image/jpeg',
        'application/vnd.openxmlformats-officedocument.presentationml.presentation')),
    evidence jsonb not null check (jsonb_typeof(evidence) = 'object'),
    state text not null default 'pending' check (state in ('pending','ready')),
    created_at timestamptz not null default clock_timestamp(),
    verified_at timestamptz,
    check (storage_key = run_id::text || '/' || id::text || '/' || sha256),
    check ((state = 'pending' and verified_at is null)
        or (state = 'ready' and verified_at is not null))
);
create index artifacts_run_idx on gtm.artifacts(run_id,created_at);
alter table gtm.artifacts enable row level security;
alter table gtm.artifacts force row level security;
revoke all on gtm.artifacts from public,anon,authenticated,service_role;
grant select on gtm.runs to gtm_worker,gtm_api;
create policy runs_worker_read on gtm.runs for select to gtm_worker using (true);
create policy runs_api_read on gtm.runs for select to gtm_api
    using (project_id in (select id from gtm.projects));
grant select,insert on gtm.artifacts to gtm_worker;
grant update(state,verified_at) on gtm.artifacts to gtm_worker;
create policy artifacts_worker_read on gtm.artifacts for select to gtm_worker using (true);
create policy artifacts_worker_insert on gtm.artifacts for insert to gtm_worker
    with check (state = 'pending' and verified_at is null);
create policy artifacts_worker_update on gtm.artifacts for update to gtm_worker
    using (true) with check (true);
grant select on gtm.artifacts to gtm_api;
create policy artifacts_api_read on gtm.artifacts for select to gtm_api
    using (state = 'ready' and run_id in (select id from gtm.runs));
comment on table gtm.artifacts is 'Private immutable content manifest. Ready only after download/hash verification. No object URLs or credentials.';
