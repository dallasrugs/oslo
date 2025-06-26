'''
    This router is for configuring Odoo Integration 
'''
from internal.connector import getOdooConnection
from fastapi import HTTPException
import requests 
import json 

class Odoo:
    def __init__(self):
        # authenticate using Odoo API
        self.odoo_url,self.cookies = getOdooConnection()
        if not self.cookies:
            raise HTTPException(status_code=500, detail=f"Failed to authenticate with Odoo API")
    

    def getUsers(self):
        # testing procedure do not use, like ever.
        try:
            # Define the URL for fetching users
            # GET /api/res.users/?query={id,name,company_id{name}}
            USERS_URL = self.odoo_url + 'api/res.users/?query={id, name, company_id{name}}'
            cookies = self.cookies  # Use the cookies obtained during authentication
            res = requests.get(
                USERS_URL, 
                cookies=cookies  # Here we are sending cookies which holds info for authenticated user
            )

            return res.json()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error fetching users from Odoo: {str(e)}")
    

    def addInquiry(self, inquiry_data: dict):
        CRM_LEAD_URL = self.odoo_url + "api/crm.lead/"

        odoo_data = {
            "name": inquiry_data.get("subject", "Website Inquiry"),
            "email_from": inquiry_data.get("email"),
            "contact_name": inquiry_data.get("contact_name"),
            "phone": inquiry_data.get("phone"),
            "description": inquiry_data.get("message"),
            "city": inquiry_data.get("city")
        }

        # Match Odoo's expected structure: {"params": {"data": {...}}}
        payload = {
            "params": {
                "data": odoo_data
            }
        }

        headers = {"Content-Type": "application/json"}

        response = requests.post(
            CRM_LEAD_URL,
            data=json.dumps(payload),  # Important: use json.dumps
            headers=headers,
            cookies=self.cookies
        )

        if response.status_code != 200:
            print("Odoo error:", response.status_code, response.text)
            raise HTTPException(status_code=response.status_code, detail=response.text)

        return response.json()
