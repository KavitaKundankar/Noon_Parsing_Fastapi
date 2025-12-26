from logger_config import logger
from .db_connect_pool import Database


def get_id(imo):

    db = Database("DB4")  # SHIPPING database
    conn = db.get_conn()
    cur = conn.cursor()

    row = None

    if imo:
        logger.info(f"Searching ID in DB")

        query = f"""
            SELECT id
            FROM {db.schema}.{db.table}
            WHERE imo = %s
            LIMIT 1;
        """
        cur.execute(query, (imo,))
        row = cur.fetchone()

    db.put_conn(conn)


    if row:
        id = row
        logger.info(f"Matched IMO: {imo}, vessel_id : {id}")
        return id

    logger.warning("No IMO match found in DB")
    return None
