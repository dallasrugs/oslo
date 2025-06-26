# file: console-api/app/internal/status.py
from internal.connector import getDBConnection, getOdooConnection
from fastapi import HTTPException
from internal.logger import logger

# Shared objects
db_engine = None
db_metadata = None
db_session = None

# instance loaders 
product_instance = None
odoo_instance = None 

def checkDBConnection():
    # declaring global variables to store the database connection details
    global engine, metadata, session
    global db_engine, db_metadata, db_session
    try:
        logger.info("Connecting to Supabase Database...")
        engine,metadata,session = getDBConnection()
        db_engine = engine 
        db_metadata = metadata 
        db_session = session
        logger.info("Supabase Database connection established successfully.")

    except Exception as e:
        logger.error(f"Error connecting to Supabase Database: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Could not connect to Supabase Database, check Exception: {str(e)}")

def checkOdooConnection():
    logger.info("Connecting to Odoo Instance")
    try:
        getOdooConnection()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not connect to Odoo, check Exception: {str(e)}")

def getLoaders():
    global product_instance
    global odoo_instance

    # Loading Product Instance 
    try:
        if product_instance is None:
            logger.info("Loading Product instance...")
            from routers.products import Product  # Delayed import to avoid circular dependency
            product_instance = Product()
    except Exception as e:
        logger.error(f"Error loading Product instance: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Could not load Product instance, check Exception: {str(e)}")
    
    # Loading Odoo Instance 
    try:
        if odoo_instance is None:
            logger.info("Loading Odoo Instance..")
            from routers.odoo import Odoo 
            odoo_instance = Odoo()
    except Exception as e:
        logger.error(f"Error Loading Odoo Connection")
        raise HTTPException(status_code=500, detail=f"Could not load Odoo instance, check Exception: {str(e)}")
    
    
def startup():
    """
    This function is called at the startup of the application.
    It checks the database connection and loads necessary instances.
    """
    checkDBConnection() # for connecting to Supabase
    checkOdooConnection() # for connecting to Odoo Service 
    getLoaders()
    logger.info("Application startup complete.")
