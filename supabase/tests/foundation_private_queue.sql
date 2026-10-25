-- Run with an administrative migration connection, never browser credentials.
-- Everything rolls back, including synthetic Auth identity and application rows.
begin;
do $$
declare
    user_ref uuid := gen_random_uuid();
    project_ref uuid;
    run_ref uuid;
    role_name text;
    table_name text;
    secured_count integer;
begin
    select count(*) into secured_count
    from pg_class c join pg_namespace n on n.oid = c.relnamespace
    where n.nspname = 'gtm' and c.relname in ('projects','runs','jobs')
        and c.relrowsecurity and c.relforcerowsecurity;
    assert secured_count = 3, 'RLS must protect every application table';

    insert into auth.users(id) values (user_ref);
    insert into gtm.projects(owner_id,title,offer_brief,product_in_development,geo)
        values(user_ref,'Synthetic database test','{}',false,'{}') returning id into project_ref;
    insert into gtm.runs(project_id,module_no,mode,cost_cap)
        values(project_ref,1,'synthetic',10) returning id into run_ref;
    insert into gtm.jobs(run_id,task_type) values(run_ref,'synthetic');
    assert (select count(*) = 1 from gtm.jobs where run_id = run_ref), 'Write/read roundtrip failed';

    begin
        insert into gtm.runs(project_id,module_no,mode,cost_cap) values(project_ref,8,'synthetic',10);
        raise exception 'Invalid module accepted';
    exception when check_violation then null;
    end;
    begin
        insert into gtm.jobs(run_id,task_type) values(gen_random_uuid(),'synthetic');
        raise exception 'Orphan job accepted';
    exception when foreign_key_violation then null;
    end;
    begin
        insert into gtm.jobs(run_id,task_type,attempt,max_attempts) values(run_ref,'synthetic',4,3);
        raise exception 'Invalid retry counter accepted';
    exception when check_violation then null;
    end;

    foreach role_name in array array['anon','authenticated','service_role'] loop
        assert not has_schema_privilege(role_name,'gtm','USAGE'), 'Unexpected schema access';
        foreach table_name in array array['projects','runs','jobs'] loop
            assert not has_table_privilege(role_name,'gtm.' || table_name,'SELECT,INSERT,UPDATE,DELETE'),
                'Unexpected table privileges';
            begin
                execute format('set local role %I',role_name);
                execute format('select * from gtm.%I limit 1',table_name);
                raise exception 'Unauthorized query succeeded';
            exception when insufficient_privilege then null;
            end;
        end loop;
    end loop;
end;
$$;
rollback;
