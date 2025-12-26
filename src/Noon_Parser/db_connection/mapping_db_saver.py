import psycopg2
import psycopg2.extras
from logger_config import logger
from .db_connect_pool import Database


def save_noon_parsing_report(data):

    query = """
        INSERT INTO configs.noon_parsing_reports (
            noonreportdata,
            templateid,
            voyage,
            vesselid,
            report_date_time_utc,
            reporttype,
            raw_data,
            parsed_data,
            report_id
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, gen_random_uuid())
        RETURNING id;
    """

    try:
        db = Database("DB5")
        conn = db.get_conn()
        cur = conn.cursor()

        cur.execute(
            query,
            (
                psycopg2.extras.Json(data.get("noonreportdata")),
                data.get("templateid"),
                data.get("voyage"),
                data.get("vesselid"),
                data.get("report_date_time_utc"),
                data.get("reporttype"),
                psycopg2.extras.Json(data.get("raw_data")),
                psycopg2.extras.Json(data.get("parsed_data"))
            )
        )

        inserted_id = cur.fetchone()[0]
        conn.commit()

        logger.info(f"Inserted noon_parsing_report ID: {inserted_id}")

        cur.close()
        conn.close()

        return inserted_id

    except Exception as e:
        logger.error(f"Error saving noon parsing report: {str(e)}")
        return None
