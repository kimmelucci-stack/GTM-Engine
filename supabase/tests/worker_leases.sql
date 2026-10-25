begin;
do $$
declare
    owner_a uuid := gen_random_uuid();
    owner_b uuid := gen_random_uuid();
    project_a uuid;
    project_b uuid;
    run_ref uuid;
    first_job gtm.jobs;
    second_job gtm.jobs;
    retry_job gtm.jobs;
begin
    insert into auth.users(id) values(owner_a),(owner_b);
    insert into gtm.projects(owner_id,title,offer_brief,product_in_development,geo)
        values(owner_a,'Synthetic A','{}',false,'{}') returning id into project_a;
    insert into gtm.projects(owner_id,title,offer_brief,product_in_development,geo)
        values(owner_b,'Synthetic B','{}',false,'{}') returning id into project_b;
    insert into gtm.runs(project_id,module_no,mode,cost_cap)
        values(project_a,1,'synthetic',10) returning id into run_ref;
    insert into gtm.jobs(run_id,task_type,max_attempts)
        values(run_ref,'synthetic',1),(run_ref,'synthetic',1),(run_ref,'unsupported',1);

    perform set_config('gtm.owner_id', '', true);
    set local role gtm_api;
    assert (select count(*) = 0 from gtm.projects), 'Missing principal exposed data';
    perform set_config('gtm.owner_id',owner_a::text,true);
    assert (select count(*) = 1 from gtm.projects), 'Tenant isolation failed';
    assert not exists(select 1 from gtm.projects where id = project_b), 'Other tenant exposed';
    insert into gtm.projects(owner_id,title,offer_brief,product_in_development,geo)
        values(owner_a,'Synthetic owned write','{}',false,'{}');
    begin
        insert into gtm.projects(owner_id,title,offer_brief,product_in_development,geo)
            values(owner_b,'Forbidden owner','{}',false,'{}');
        raise exception 'Owner spoof accepted';
    exception when insufficient_privilege then null;
    end;
    begin
        perform gtm.expire_jobs();
        raise exception 'API accessed worker function';
    exception when insufficient_privilege then null;
    end;
    reset role;

    set local role gtm_worker;
    begin
        perform id from gtm.projects;
        raise exception 'Worker read private brief';
    exception when insufficient_privilege then null;
    end;
    select * into first_job from gtm.claim_job(array['synthetic']);
    select * into second_job from gtm.claim_job(array['synthetic']);
    assert first_job.id <> second_job.id, 'Same job assigned twice';
    assert first_job.attempt = 1, 'Attempt not persisted';
    assert not exists(select 1 from gtm.claim_job(array['synthetic'])), 'Unsupported work claimed';
    assert not gtm.heartbeat_job(first_job.id,gen_random_uuid()), 'Wrong heartbeat token accepted';
    assert gtm.heartbeat_job(first_job.id,first_job.lease_token), 'Heartbeat failed';
    assert not gtm.finish_job(first_job.id,gen_random_uuid(),'completed'), 'Wrong finish token accepted';
    assert gtm.finish_job(first_job.id,first_job.lease_token,'completed'), 'Completion failed';
    assert not gtm.finish_job(first_job.id,first_job.lease_token,'completed'), 'Stale completion accepted';

    update gtm.jobs set lease_expires_at = clock_timestamp() - interval '1 second'
        where id = second_job.id;
    assert not gtm.heartbeat_job(second_job.id,second_job.lease_token), 'Expired lease renewed';
    assert not gtm.finish_job(second_job.id,second_job.lease_token,'completed'), 'Expired completion accepted';
    assert gtm.expire_jobs() = 1, 'Timeout cleanup failed';
    assert exists(select 1 from gtm.jobs where id = second_job.id and state = 'failed'
        and error_code = 'outcome_unknown'), 'Uncertain job retried';
    reset role;

    insert into gtm.jobs(run_id,task_type,max_attempts) values(run_ref,'retry_test',1);
    set local role gtm_worker;
    select * into retry_job from gtm.claim_job(array['retry_test']);
    assert gtm.finish_job(retry_job.id,retry_job.lease_token,'queued','retry_safe');
    assert exists(select 1 from gtm.jobs where id = retry_job.id and state = 'failed'),
        'Retry cap not enforced';
    begin
        perform gtm.claim_job(array['synthetic'],0);
        raise exception 'Invalid lease accepted';
    exception when raise_exception then
        if sqlerrm <> 'invalid_lease_duration' then raise; end if;
    end;
    reset role;
end;
$$;
rollback;
