import json
import re
import os
from datetime import datetime
from ..logger_config import logger
from ..config import BASE_DIR
from ..db_connection.mapping_loader import get_standard_keys
from ..db_connection.save_unmapped import merge_unmapped_keys


class NoonReportMapper:
    def __init__(self):
        pass

    def map(self, parsed_mail: dict, tenant: str, imo : str, name : str):

        try:
            final_mapping = {}
            unmapped={}
            standard_data = {}

            standard_data = get_standard_keys(tenant)

            # Perform mapping
            for key, value in parsed_mail.items():

                if value is None or value == "" or value == "0" or value == 0:           # To skip null values
                    continue

                if key in standard_data:
                    mapped_key = standard_data[key]
                    final_mapping[mapped_key] = value

                else :
                    unmapped[key] = value
   
            merge_unmapped_keys(unmapped, tenant)

            logger.error(f"Saved Unmapped keys for tenant {tenant} : {unmapped}")

            final_mapping.update(unmapped)


            logger.info(f"Mapping done for tenant : '{tenant}',  IMO : '{imo}' vessel : '{name}'")
            
            return final_mapping

        except Exception as e:
            logger.error(f"Error in mapping. No mapping was saved for tenant : '{tenant}', IMO : '{imo}', vessel : '{name}' : {e}")
            return {}
        
















# path = os.path.join(BASE_DIR, "mapping","json_mappings", f"{tenant}_mapping.json")

# if not os.path.exists(path):
#     logger.error(f"Mapping file not found for tenant: {tenant}")
#     return {}

# with open(path, "r") as f:
#     standard_data = json.load(f)