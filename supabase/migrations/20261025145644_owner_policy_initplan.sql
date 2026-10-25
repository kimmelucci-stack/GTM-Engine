-- Keep the setting lookup in its own initplan, outside the UUID conversion.
alter policy projects_api_read on gtm.projects
    using (owner_id = nullif((select current_setting('gtm.owner_id',true)),'')::uuid);
alter policy projects_api_create on gtm.projects
    with check (owner_id = nullif((select current_setting('gtm.owner_id',true)),'')::uuid);
