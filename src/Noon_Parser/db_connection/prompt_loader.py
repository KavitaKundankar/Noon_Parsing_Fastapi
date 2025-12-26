from .db_connect_pool import Database
from logger_config import logger


def get_tenant_prompt(tenant, imo):
    db = Database("DB3")   # configs.noon_tenant_prompts
    db2 = Database("DB2")
    conn = db.get_conn()
    cur = conn.cursor()

    # Fetch STANDARD prompt (always)
    cur.execute(f"""
        SELECT prompt 
        FROM {db.schema}.{db.table}
        WHERE tenant = 'standard'
        LIMIT 1;
    """)
    standard_prompt_row = cur.fetchone()
    standard_prompt = standard_prompt_row[0] if standard_prompt_row else ""

    # Fetch TENANT-specific prompt
    tenant_prompt = ""
    tenant_parsed_keys = ""

    # Initialize vessel-specific variables
    vessel_prompt = ""
    vessel_keys = ""

    if tenant:
        logger.info(f"Searching tenant in DB: {tenant}")

        cur.execute(f"""
            SELECT prompt, parsed_keys
            FROM {db.schema}.{db.table}
            WHERE tenant = %s
            LIMIT 1;
        """, (tenant,))
        tenant_row = cur.fetchone()

        if tenant_row:
            tenant_prompt = tenant_row[0] or ""
            tenant_parsed_keys = tenant_row[1] or ""
    
    if imo : 
        logger.info(f"Searching imo prompt in DB: {imo}")

        cur.execute(f"""
            SELECT vessel_prompt, vessel_keys
            FROM {db2.schema}.{db2.table}
            WHERE vessel_imo = %s
            LIMIT 1;
        """, (imo,))
        imo_row = cur.fetchone()

        if imo_row:
            vessel_prompt = imo_row[0] or ""
            vessel_keys = imo_row[1] or ""

    db.put_conn(conn)

    return standard_prompt, tenant_prompt, tenant_parsed_keys, vessel_prompt, vessel_keys

