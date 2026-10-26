-- Opt-in live fixture, synthetic only. Save returned metadata under ignored artifacts/private/.
-- After the live suite, remove only this exact synthetic project/user tree.
with u as (
    insert into auth.users(id,aud,role)
    values(gen_random_uuid(),'authenticated','authenticated') returning id
), p as (
    insert into gtm.projects(owner_id,title,offer_brief,product_in_development,geo)
    select id,'Synthetic private archive test','{}',true,'{}' from u returning id,owner_id
), r as (
    insert into gtm.runs(project_id,module_no,mode,cost_cap)
    select p.id,1,'synthetic-storage',1 from p cross join generate_series(1,2)
    returning id,project_id
), j as (
    insert into gtm.jobs(run_id,task_type,max_attempts)
    select id,case when row_number() over(order by id)=1 then 'catalog.archive'
        else 'artifact.synthetic' end,1 from r returning id,run_id,task_type
)
select (select owner_id from p) as owner_id,(select id from p) as project_id,
    json_agg(j) as jobs from j;
