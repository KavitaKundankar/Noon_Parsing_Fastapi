from .db_connect_pool import Database
from ..vessel_info.vessel_info import extract_vessel_metadata
from ..logger_config import logger


def get_standard_keys(tenant):
    db = Database("DB3")   # configs.noon_tenant_prompts
    conn = db.get_conn()
    cur = conn.cursor()

    # Fetch STANDARD prompt (always)
    cur.execute(f"""
        SELECT standard_mapping 
        FROM {db.schema}.{db.table}
        WHERE tenant = %s
        LIMIT 1;
    """, (tenant,))
    
    standard_keys_row = cur.fetchone()
    standard_keys = standard_keys_row[0] if standard_keys_row else "{}"

    db.put_conn(conn)
    return standard_keys