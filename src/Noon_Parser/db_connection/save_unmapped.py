import json
from logger_config import logger
from .db_connect_pool import Database


def merge_unmapped_keys(unmapped: dict, tenant: str):
    try:
        db = Database("DB3")
        conn = db.get_conn()
        cur = conn.cursor()

        query = """
            UPDATE configs.noon_tenant_prompts
            SET unmapped_keys = COALESCE(unmapped_keys, '{}'::jsonb) || %s::jsonb
            WHERE tenant = %s;
        """

        cur.execute(query, (json.dumps(unmapped), tenant))

        conn.commit()

        logger.info(f"Merged unmapped keys for tenant: {tenant}")

        cur.close()
        conn.close()

    except Exception as e:
        logger.error(f"Error merging unmapped keys into DB: {str(e)}")