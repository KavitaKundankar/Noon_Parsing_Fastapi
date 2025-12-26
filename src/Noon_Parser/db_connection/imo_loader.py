from .db_connect_pool import Database
from ..vessel_info.vessel_info import extract_vessel_metadata
from logger_config import logger


def get_imo(message):

    ids = extract_vessel_metadata(message)
    imo = ids.get("imo_number")
    vessel_name = ids.get("vessel_name")

    db = Database("DB2")  # SHIPPING database
    conn = db.get_conn()
    cur = conn.cursor()

    row = None

    if imo:
        logger.info(f"Searching IMO in DB: {imo}")

        query = f"""
            SELECT vessel_imo, vessel
            FROM {db.schema}.{db.table}
            WHERE vessel_imo = %s
            LIMIT 1;
        """
        cur.execute(query, (imo,))
        row = cur.fetchone()

    elif vessel_name:
        logger.info(f"Searching Vessel Name in DB: {vessel_name}")

        query = f"""
            SELECT vessel_imo, vessel
            FROM {db.schema}.{db.table}
            WHERE LOWER(vessel) = LOWER(%s)
            LIMIT 1;
        """
        cur.execute(query, (vessel_name,))
        row = cur.fetchone()

    db.put_conn(conn)


    if row:
        db_imo,  name = row
        logger.info(f"Matched IMO: {db_imo}, Vessel: {name}")
        return db_imo, name

    logger.warning("No IMO match found in DB")
    return None, None
