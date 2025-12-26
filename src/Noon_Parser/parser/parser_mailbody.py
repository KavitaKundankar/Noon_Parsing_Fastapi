import google.generativeai as genai
import json, re
import os
from datetime import datetime
from ..logger_config import logger
from ..config import BASE_DIR
from ..db_connection.prompt_loader import get_tenant_prompt
import json
from dotenv import load_dotenv

load_dotenv()

class NoonReportParser:

    def __init__(self, api_key):

        Gemini_model = os.getenv("Gemini_model")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(Gemini_model)
        

    def parse(self, body, tenant, imo):

        standard_prompt, tenant_prompt, parsed_keys, vessel_prompt, vessel_keys = get_tenant_prompt(tenant, imo)

        # Build final prompt
        final_prompt = ""

        if standard_prompt:
            final_prompt += f"{standard_prompt}\n\n"

        if tenant_prompt:
            final_prompt += f"{tenant_prompt}\n\n"

        if parsed_keys:
            final_prompt += f"{parsed_keys}\n\n"

        if vessel_keys:
            final_prompt += f"{vessel_keys}\n\n"

        if vessel_prompt:
            final_prompt += f"{vessel_prompt}\n\n"

        
        final_prompt += f"EMAIL CONTENT:\n{body}"

        response = self.model.generate_content(final_prompt)

        logger.info(f"Token usage: {response.usage_metadata}")

        cleaned = re.sub(r"^```json\s*|\s*```$", "", response.text.strip())


        parsed_mail = json.loads(cleaned)

        try:
            parsed_mail = json.loads(cleaned)
        except Exception as e:
            logger.error(f"Invalid JSON in save(): {e}\nDATA={cleaned}")

        return parsed_mail
