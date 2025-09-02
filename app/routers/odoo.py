'''
    This router is for configuring Odoo Integration 
'''
from internal.connector import getOdooConnection
from fastapi import HTTPException
import requests 
import json 
from internal.logger import logger
from datetime import datetime

class Odoo:
    def __init__(self):
        self._authenticate()

    def _authenticate(self):
        self.odoo_url, self.cookies = getOdooConnection()
        if not self.cookies:
            raise HTTPException(status_code=500, detail="Failed to authenticate with Odoo API")

    def _reauthenticate_and_retry(self, func, *args, **kwargs):
        # Call the function, retry once after re-authentication if it fails
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # Optional: You can inspect the exception or error code here
            logger.info("Relogging again due to auth failure earlier.")
            self._authenticate()  # Re-authenticate
            return func(*args, **kwargs)  # Retry
    


    def getUsers(self):
        # avoid this method, use only when needed
        def fetch_users():
            USERS_URL = self.odoo_url + 'api/res.users/?query={id, name, company_id{name}}'
            res = requests.get(USERS_URL, cookies=self.cookies)
            if res.status_code == 401:
                raise Exception("Unauthorized")
            return res.json()

        return self._reauthenticate_and_retry(fetch_users)
    

    def addInquiry(self, inquiry_data: dict):
        def post_inquiry():
            CRM_LEAD_URL = self.odoo_url + "api/crm.lead/"

            odoo_data = {
                "name": inquiry_data.get("subject", "Website Inquiry"),
                "email_from": inquiry_data.get("email"),
                "contact_name": inquiry_data.get("contact_name"),
                "phone": inquiry_data.get("phone"),
                "description": inquiry_data.get("message"),
                "probability": 50,
                "create_date": datetime.now().isoformat()
            }

            payload = {
                "params": {
                    "data": odoo_data
                }
            }

            headers = {"Content-Type": "application/json"}

            response = requests.post(
                CRM_LEAD_URL,
                data=json.dumps(payload),
                headers=headers,
                cookies=self.cookies
            )

            if response.status_code == 401:
                raise Exception("Unauthorized")
            
            return response.json()

        return self._reauthenticate_and_retry(post_inquiry)
            


