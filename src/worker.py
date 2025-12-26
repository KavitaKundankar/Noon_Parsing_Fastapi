import asyncio
import os
import json
from .daily_limit import DailyLimitManager
from .load_redis_config import reconcile_worker_resources
import config as default_config
from .Noon_Parser.vessel_info.vessel_info import extract_vessel_metadata
from .Noon_Parser.db_connection.imo_loader import get_imo
from .Noon_Parser.db_connection.vessel_id import get_id
from .Noon_Parser.parser.parser_mailbody import NoonReportParser
from .Noon_Parser.mapping.mapping_mailbody import NoonReportMapper
from .Noon_Parser.mapping.mapping_db import build_noon_parsing_payload
from .Noon_Parser.db_connection.mapping_db_saver import save_noon_parsing_report

# Shared state
limit_manager = DailyLimitManager(limit=default_config.DAILY_LIMIT)

async def rabbit_worker():
    """Background task that consumes messages from RabbitMQ."""
    print("🚀 Starting RabbitMQ Worker (Clean Refactored Mode)...")
    
    # Initialize Parser and Mapper
    api_key = os.getenv("GEMINI_API_KEY")
    parser = NoonReportParser(api_key=api_key)
    mapper = NoonReportMapper()

    rabbit = None
    channel = None
    queue = None
    current_cfg = None

    while True:
        try:
            # 1. Handle daily sleep/cooldown
            await limit_manager.check_and_wait()

            # 2. Reconcile settings and connections (Redis + RabbitMQ)
            current_cfg, rabbit, channel, queue = await reconcile_worker_resources(
                current_cfg, limit_manager, rabbit, channel, queue
            )

            # 3. If reconciliation failed (e.g. Redis/Rabbit down), wait and retry
            if not queue:
                continue

            # 4. Pull and process message
            message = await queue.get(fail=False)

            if message:
                async with message.process(requeue=True):
                    raw_body = message.body.decode()
                    print(f"📩 Processing message (length: {len(raw_body)})...")
                    
                    try:
                        msg = json.loads(raw_body)
                        subject = msg.get("subject", "No Subject")
                        content = msg.get("body", raw_body)
                        tenant = msg.get("tenant", "standard")
                    except json.JSONDecodeError:
                        # Fallback if message is not JSON
                        subject = "No Subject"
                        content = raw_body
                        tenant = "standard"

                    mail_body_str = f"Subject: {subject}\nMail_body: {content}"
                    
                    # -------------------------
                    # Main processing flow
                    # -------------------------
                    # 1. Match IMO/Vessel
                    result = get_imo(mail_body_str)
                    
                    if result is None or result == (None, None):
                        print(f"⚠️ Vessel not found in DB for tenant {tenant}. Using standards.")
                        vessel_imo = None
                        vessel_name = "Unknown"
                    else:
                        vessel_imo, vessel_name = result

                    # 2. AI Parse
                    parsed = parser.parse(mail_body_str, tenant, vessel_imo)

                    # 3. Data Map
                    mapped = mapper.map(parsed, tenant, vessel_imo, vessel_name)

                    # 4. Get vessel_id
                    vessel_id = get_id(vessel_imo)

                    # 5. Build Payload and Save
                    payload = build_noon_parsing_payload(
                        mapped,
                        tenant,
                        vessel_id,
                        mail_body_str,
                        vessel_name,
                        parsed
                    )

                    if payload:
                        report_id = save_noon_parsing_report(payload)
                        print(f"✅ Report saved successfully. ID: {report_id}")
                    
                    await asyncio.sleep(1) 

                print("✅ Message ACKed.")
                limit_manager.increment()
            else:
                # Idle wait if queue is empty
                await asyncio.sleep(5)

        except asyncio.CancelledError:
            print("🛑 Worker task cancelled.")
            break
        except Exception as e:
            print(f"❌ Worker loop error: {e}")
            current_cfg = None # Reset to trigger full recovery
            await asyncio.sleep(10)
