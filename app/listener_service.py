import time      # Import time for keeping the background thread alive
from internal.logger import logger
from internal.connector import connectRealtime
from datetime import datetime
import requests
import asyncio


def convert_datetime(obj):
    if isinstance(obj, dict):
        return {k: convert_datetime(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_datetime(i) for i in obj]
    elif isinstance(obj, datetime):
        return obj.isoformat()
    else:
        return obj

async def start_supabase_listener_service():
    try:
        supabase_client = await connectRealtime()
        logger.info("Starting Supabase real-time listener...")

        await supabase_client.channel('schema-db-changes').on_postgres_changes(
            event="INSERT",
            schema="public",
            table="inquiry",
            callback=handle_supabase_insert_event
        ).subscribe()

        logger.info("Supabase real-time listener subscribed. Keeping thread alive...")

        while True:
            await asyncio.sleep(60)

    except Exception as e:
        logger.error(f"Critical error in Supabase listener service: {str(e)}")


def handle_supabase_insert_event(payload):
    print(f"Supabase INSERT event received: {payload}")

    try:
        new_record = payload.get("data", {}).get("record", {})
        print(new_record)
        if not new_record:
            logger.info("⚠️ No 'record' found in payload.")
            return

        # Recursively convert all datetime objects to strings
        new_record = convert_datetime(new_record)

        logger.info(f"✅ New Inquiry Received from Supabase: {new_record}")

        subject = new_record.get("subject", "No Subject")
        email = new_record.get("email", "no_email@example.com")
        contact_name = new_record.get("name", "Unknown Contact")
        phone = new_record.get("phone", "N/A")
        message = new_record.get("message", "No message provided.")

        odoo_inquiry_url = "http://localhost:8000/api/v1/odoo/inquiry"

        request_body = {
            "subject": subject,
            "email": email,
            "contact_name": contact_name,
            "phone": phone,
            "message": message,
        }

        print(f"📡 Sending POST request to: {odoo_inquiry_url}")
        response = requests.post(odoo_inquiry_url, json=request_body)
        response.raise_for_status()

        print(f"✅ POST to Odoo successful! Status: {response.status_code}")
        print(f"🔁 Response from Odoo: {response.json()}")

    except requests.exceptions.HTTPError as http_err:
        print(f"❌ HTTP error while sending to Odoo: {http_err} - {response.text}")
    except requests.exceptions.ConnectionError as conn_err:
        print(f"❌ Connection error while sending to Odoo: {conn_err}")
    except requests.exceptions.Timeout as timeout_err:
        print(f"⏱ Timeout error while sending to Odoo: {timeout_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"❗ Unexpected error while sending to Odoo: {req_err}")
    except Exception as e:
        print(f"🔥 Unexpected error in handler: {str(e)}")



if __name__ == "__main__":
    try:
        asyncio.run(start_supabase_listener_service())
    except KeyboardInterrupt:
        logger.info("Listener stopped by user.")
