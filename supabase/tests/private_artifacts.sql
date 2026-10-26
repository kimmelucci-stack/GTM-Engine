-- Hosted SQL assertions. No private content or credentials, no persistent changes.
begin;
do $$
declare role_name text;
begin
    if not exists (select 1 from pg_class c join pg_namespace n on n.oid=c.relnamespace
        where n.nspname='gtm' and c.relname='artifacts' and c.relrowsecurity
            and c.relforcerowsecurity) then
        raise exception 'artifact_rls_missing';
    end if;
    foreach role_name in array array['anon','authenticated','service_role'] loop
        if has_table_privilege(role_name,'gtm.artifacts','SELECT')
            or has_table_privilege(role_name,'gtm.artifacts','INSERT') then
            raise exception 'client_manifest_access';
        end if;
    end loop;
    if has_table_privilege('gtm_api','gtm.artifacts','INSERT')
        or has_table_privilege('gtm_worker','gtm.artifacts','DELETE')
        or has_column_privilege('gtm_worker','gtm.artifacts','sha256','UPDATE')
        or has_column_privilege('gtm_worker','gtm.artifacts','storage_key','UPDATE')
        or has_column_privilege('gtm_worker','gtm.artifacts','evidence','UPDATE') then
        raise exception 'manifest_mutation_permissions';
    end if;
    if exists(select 1 from storage.buckets where id='gtm-evidence' and public) then
        raise exception 'public_evidence_bucket';
    end if;
end $$;
rollback;
