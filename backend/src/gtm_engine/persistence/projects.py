"""Project access always receives a verified owner from the authentication boundary."""

from uuid import UUID

from psycopg.types.json import Jsonb

from gtm_engine.persistence.database import connection


def create_project(owner_id: UUID, values: dict) -> dict:
    with connection("gtm_api", owner_id) as conn:
        return conn.execute(
            """insert into gtm.projects
               (owner_id,title,offer_brief,product_in_development,geo,locale)
               values (%s,%s,%s,%s,%s,%s)
               returning id,title,offer_brief,product_in_development,geo,locale,created_at""",
            (owner_id, values["title"], Jsonb(values["offer_brief"]),
             values["product_in_development"], Jsonb(values["geo"]), values["locale"]),
        ).fetchone()


def get_project(owner_id: UUID, project_id: UUID) -> dict | None:
    with connection("gtm_api", owner_id) as conn:
        return conn.execute(
            """select id,title,offer_brief,product_in_development,geo,locale,created_at
               from gtm.projects where id = %s and owner_id = %s""",
            (project_id, owner_id),
        ).fetchone()
