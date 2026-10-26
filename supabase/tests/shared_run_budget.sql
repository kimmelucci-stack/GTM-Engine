-- Administrative connection, synthetic identities only, no persistent fixtures.
begin;
do $$
declare
    owner_ref uuid := gen_random_uuid();
    project_ref uuid;
    budget_ref uuid;
    run_ref uuid;
    actor text;
begin
    assert (select count(*) = 2 from pg_class c join pg_namespace n on n.oid=c.relnamespace
        where n.nspname='gtm' and c.relname in ('budgets','cost_events')
            and c.relrowsecurity and c.relforcerowsecurity), 'RLS missing';
    insert into auth.users(id) values(owner_ref);
    insert into gtm.projects(owner_id,title,offer_brief,product_in_development,geo)
        values(owner_ref,'Synthetic budget constraints','{}',false,'{}') returning id into project_ref;
    insert into gtm.budgets(project_id,cap_usd) values(project_ref,15) returning id into budget_ref;
    insert into gtm.runs(project_id,budget_id,module_no,mode,cost_cap)
        values(project_ref,budget_ref,1,'synthetic',15) returning id into run_ref;
    begin
        insert into gtm.budgets(project_id,cap_usd) values(project_ref,16);
        raise exception 'Cap above 15 accepted';
    exception when check_violation then null;
    end;
    begin
        insert into gtm.cost_events(budget_id,event_id,run_id,provider,endpoint,component,
            ceiling_usd,actual_usd,status,settled_at)
        values(budget_ref,'invalid-nan',run_ref,'synthetic','/test','data',1,'NaN','settled',now());
        raise exception 'NaN actual accepted';
    exception when check_violation then null;
    end;
    foreach actor in array array['anon','authenticated','service_role','gtm_api'] loop
        assert not has_table_privilege(actor,'gtm.cost_events','SELECT,INSERT,UPDATE,DELETE'),
            'Unexpected cost privileges';
        begin
            execute format('set local role %I',actor);
            perform * from gtm.cost_events limit 1;
            raise exception 'Unauthorized cost access';
        exception when insufficient_privilege then null;
        end;
    end loop;
    perform set_config('gtm.owner_id',owner_ref::text,true);
    set local role gtm_api;
    assert (select count(*)=1 from gtm.budgets), 'Budget owner isolation failed';
    begin
        insert into gtm.budgets(project_id,cap_usd,halted) values(project_ref,10,true);
        raise exception 'Unexpected initial budget state accepted';
    exception when insufficient_privilege then null;
    end;
    reset role;
    set local role gtm_worker;
    begin
        update gtm.budgets set cap_usd=14 where id=budget_ref;
        raise exception 'Worker changed approved cap';
    exception when insufficient_privilege then null;
    end;
    begin
        delete from gtm.cost_events where budget_id=budget_ref;
        raise exception 'Worker deleted cost history';
    exception when insufficient_privilege then null;
    end;
    reset role;
end;
$$;
rollback;
