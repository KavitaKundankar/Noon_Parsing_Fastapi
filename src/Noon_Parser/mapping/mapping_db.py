from logger_config import logger

def build_noon_parsing_payload(mapped, tenant, vessel_id, raw_mail_body, vessel_name, parsed):

    try:
        data = {
            "noonreportdata": mapped, 
            "templateid": tenant + "_" + vessel_name, 
            "voyage": mapped.get("Voyage_Number"),
            "vesselid": vessel_id,
            "report_date_time_utc": mapped.get("Report_Date_Time"),
            "reporttype": mapped.get("Report_Type"),
            "raw_data": raw_mail_body,
            "parsed_data" : parsed
        }

        return data

    except Exception as e:
        logger.error(f"Error building noon parsing payload: {e}")
        return None
