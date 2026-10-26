-- Opt-in synthetic fixtures for test_budget_postgres_live.py.
-- Run through the administrative MCP connection. Save returned fixture JSON only
-- under artifacts/private/, then delete this synthetic tree after the tests.
with u as (
    insert into auth.users(id) values(gen_random_uuid()) returning id
), p as (
    insert into gtm.projects(owner_id,title,offer_brief,product_in_development,geo)
    select id,'Synthetic budget concurrency tests','{}',false,'{}' from u returning id,owner_id
), seeds as materialized (
    select name,gen_random_uuid() as id,requests from (values
        ('parallel',100),('duplicate',100),('uncertain',100),('overrun',100),
        ('reconcile',100),('components',100),('limits',1),('modules',100),('fk',100),('wrapper',100)
    ) v(name,requests)
), b as (
    insert into gtm.budgets(id,project_id,cap_usd,max_requests)
    select s.id,p.id,15,s.requests from seeds s cross join p returning id,project_id
), r as (
    insert into gtm.runs(project_id,budget_id,module_no,mode,cost_cap)
    select b.project_id,b.id,n,'synthetic',15 from b join seeds s on s.id=b.id
    cross join lateral generate_series(1,case when s.name='modules' then 7 else 2 end) n
    returning id,budget_id,module_no
)
select jsonb_build_object('owner_id',p.owner_id,'project_id',p.id,'cases',(
    select jsonb_agg(jsonb_build_object('name',s.name,'budget_id',b.id,'runs',(
        select jsonb_agg(r.id order by r.module_no) from r where r.budget_id=b.id
    ))) from b join seeds s on s.id=b.id
)) as fixture from p;
