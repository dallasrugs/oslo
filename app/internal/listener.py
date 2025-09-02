# listener.py
import time      # Import time for keeping the background thread alive
from internal.logger import logger
from internal.connector import connectRealtime
import requests
import asyncio



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

        # ❗ Fix: Use asyncio.sleep instead of blocking sleep
        while True:
            await asyncio.sleep(60)

    except Exception as e:
        logger.error(f"Critical error in Supabase listener service: {str(e)}")


def handle_supabase_insert_event(payload):
    """
    This callback function is executed when a new INSERT event is received from Supabase.
    It reads the new record and calls a POST request to the Odoo inquiry endpoint.
    """
    print(f"Supabase INSERT event received: {payload}")

    try:
        new_record = payload.get("data", {}).get("record", {})
        print(new_record)
        if not new_record:
            logger.info("⚠️ No 'record' found in payload.")
            return

        logger.info(f"✅ New Inquiry Received from Supabase: {new_record}")

        # Extract details from the new record
        subject = new_record.get("subject", "No Subject")
        email = new_record.get("email", "no_email@example.com")
        contact_name = new_record.get("name", "Unknown Contact")  # corrected key
        phone = new_record.get("phone", "N/A")  # ensure this exists in DB
        message = new_record.get("message", "No message provided.")

        # URL to your Odoo API
        odoo_inquiry_url = "http://localhost:8000/api/v1/odoo/inquiry"

        # Construct payload
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
