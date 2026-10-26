-- Synthetic aggregation/permission assertions with rollback; no Storage/provider calls.
begin;
do $$
declare u uuid := gen_random_uuid(); p uuid; r uuid; a uuid; b uuid; budget uuid;
begin
    insert into auth.users(id,aud,role) values(u,'authenticated','authenticated');
    insert into gtm.projects(owner_id,title,offer_brief,product_in_development,geo)
        values(u,'Synthetic aggregation','{}',true,'{}') returning id into p;
    insert into gtm.runs(project_id,module_no,mode,cost_cap)
        values(p,1,'synthetic-aggregate',1) returning id into r;
    insert into gtm.jobs(run_id,task_type) values(r,'synthetic.one') returning id into a;
    insert into gtm.jobs(run_id,task_type) values(r,'synthetic.two') returning id into b;
    update gtm.jobs set state='running',attempt=1,lease_token=gen_random_uuid(),
        lease_expires_at=clock_timestamp()+interval '1 minute' where id=a;
    if (select status from gtm.runs where id=r)<>'running' then
        raise exception 'running_aggregate_failed';
    end if;
    update gtm.jobs set state='completed',lease_token=null,lease_expires_at=null where id=a;
    if (select status from gtm.runs where id=r)<>'queued' then
        raise exception 'pending_job_was_hidden';
    end if;
    update gtm.jobs set state='failed',attempt=1 where id=b;
    if not exists(select 1 from gtm.runs where id=r and status='partial'
        and started_at is not null and completed_at>=started_at) then
        raise exception 'partial_aggregate_failed';
    end if;
    update gtm.jobs set state='running',lease_token=gen_random_uuid(),
        lease_expires_at=clock_timestamp()-interval '1 second' where id=a;
    perform gtm.expire_jobs();
    if (select status from gtm.runs where id=r)<>'failed' then
        raise exception 'expired_aggregate_failed';
    end if;
    if has_column_privilege('gtm_api','gtm.runs','status','UPDATE')
        or has_table_privilege('gtm_api','gtm.jobs','UPDATE')
        or has_function_privilege('gtm_api','gtm.claim_job(text[],integer)','EXECUTE')
        or has_column_privilege('gtm_worker','gtm.runs','project_id','UPDATE') then
        raise exception 'unsafe_run_permissions';
    end if;
    insert into gtm.budgets(project_id,cap_usd) values(p,1) returning id into budget;
    perform set_config('gtm.owner_id',u::text,true);
    set local role gtm_api;
    begin
        insert into gtm.runs(project_id,module_no,mode,cost_cap,budget_id,request_id)
            values(p,1,'provider.billable',1,budget,gen_random_uuid());
        raise exception 'arbitrary_operation_allowed';
    exception when insufficient_privilege then null;
    end;
    begin
        insert into gtm.runs(project_id,module_no,mode,cost_cap,budget_id,request_id,status)
            values(p,1,'foundation:catalog.validate',1,budget,gen_random_uuid(),'completed');
        raise exception 'spoofed_completion_allowed';
    exception when insufficient_privilege then null;
    end;
    begin
        insert into gtm.jobs(run_id,task_type) values(r,'provider.billable');
        raise exception 'arbitrary_job_allowed';
    exception when insufficient_privilege then null;
    end;
    reset role;
end $$;
rollback;
