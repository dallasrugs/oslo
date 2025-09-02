# file: console-api/app/internal/connector.py

import sqlalchemy as db 
from datetime import datetime 
from sqlalchemy.dialects import postgresql
from fastapi import HTTPException
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker
from internal.logger import logger 
from supabase import create_client, Client
from supabase import acreate_client, AsyncClient
from typing import Optional
import os 
import requests 
import json 
import asyncio

# Load environment variables from .env file
env_path = '../app/.env'
load_dotenv(env_path)

# Instantiate the database connection class
'''
This class is used to connect to the GSBAN Sourcing database.
Usage:
from console_api.app.internal.db import SourcingDB - to import the class 
'''

def getSupabaseConnection():
    try:
        logger.info("Attempting Supabase Connection..")

        connection_string = os.getenv("DATABASE_URL")

        engine = db.create_engine(connection_string, echo=True)
        
        Session = sessionmaker(bind=engine)

        session = Session()    

        connection = engine.connect()
        metadata = db.MetaData(schema=os.getenv("DATABASE_SCHEMA"))
        metadata.reflect(bind=engine)
        return [engine,metadata,session]
    
    except Exception as e:
        print(f"Error connecting to the database: {str(e)}")
        print(f"Database connection error:",{str(e)})

def getSupabase():
    return os.getenv("DATABASE_SCHEMA")

async def connectRealtime():
    try:
        url: str = os.environ.get("SUPABASE_URL")
        key: str = os.environ.get("SUPABASE_KEY")
        supabase: AsyncClient = await acreate_client(url,key)
        return supabase
    except Exception as e:
        logger.error("Failed to connect to realtime")
        raise Exception(f"Failed to connect to realtime, \n {e}")
    
def getSupabaseBucket():
    try:
        url: str = os.getenv("SUPABASE_URL")
        key: str = os.getenv("SUPABASE_KEY")
        supabase: Client = create_client(url, key)
        return supabase 
    except:
        print("Error Connecting to Supabase Bucket")

def getOdooConnection():
    try:
        AUTH_URL = os.getenv("ODOO_URL") + 'web/session/authenticate'
        headers = {'Content-Type': 'application/json'}
        # Authentication credentials
        data = {
            'params': {
                'login': os.getenv("ODOO_API_USER"),
                'password': os.getenv("ODOO_API_PWD"),
                'db': os.getenv("ODOO_DB")
            }
        }

        # Authenticate user
        res = requests.post(
            AUTH_URL, 
            data=json.dumps(data), 
            headers=headers
        )

        # Get response cookies
        # This hold information for authenticated user
        cookies = res.cookies

        return [os.getenv('ODOO_URL'),cookies] 
    
    except Exception as e:
        print(f"Error connecting to Odoo: {str(e)}")
        print(f"Odoo connection error: {str(e)}")

