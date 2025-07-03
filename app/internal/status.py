# file: console-api/app/internal/status.py
from internal.connector import getSupabaseConnection, getOdooConnection
from fastapi import HTTPException
from internal.logger import logger
from fastapi.responses import JSONResponse
from internal.connector import getSupabaseBucket

# Database shared objects
db_engine = None
db_metadata = None
db_session = None

# instance loaders 
supabase_instance = None
odoo_instance = None 

def checkSupabaseConnection():
    # declaring global variables to store the database connection details
    global engine, metadata, session
    global db_engine, db_metadata, db_session
    try:
        logger.info("Connecting to Supabase Database...")
        engine,metadata,session = getSupabaseConnection()
        db_engine = engine 
        db_metadata = metadata 
        db_session = session

    except Exception as e:
        logger.error(f"Error connecting to Supabase Database: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail= f"Could not connect to Odoo. Please check your configuration and try again. Please find the attached exception. \n {str(e)}"
        )

def checkOdooConnection():
    logger.info("Connecting to Odoo Instance")
    try:
        getOdooConnection()
    except Exception as e:
        logger.error(f"Issue with connecting to Odoo Instance: \n{str(e)}")
        return JSONResponse(status_code=500,content={"error":{
            "message": "Issue with connecting to Odoo",
            "Exception Message" : e
        }})

def getLoaders():
    global supabase_instance
    global odoo_instance
    global supabase_bucket_instance

    # Loading Supabase Instance 
    try:
        if supabase_instance is None:
            logger.info("Loading Supabase instance...")
            from routers.supabase import Supabase  # Delayed import to avoid circular dependency
            supabase_instance = Supabase()

    except Exception as e:
        logger.error(f"Error loading Supabase instance: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to load Supabase instance."
        )
    
    # Loading Odoo Instance 
    try:
        if odoo_instance is None:
            logger.info("Loading Odoo Instance..")
            from routers.odoo import Odoo 
            odoo_instance = Odoo()
    except Exception as e:
        logger.error(f"Error Loading Odoo Connection")
        raise HTTPException(
            status_code=500,
            detail="Failed to load Odoo instance."
        )
    
    
    
def startup():
    """
    This function is called at the startup of the application.
    It checks the database connection and loads necessary instances.
    """
    try:
        checkSupabaseConnection() # for connecting to Supabase
        checkOdooConnection() # for connecting to Odoo Service 
        getLoaders() # loads instance objects 
        logger.info("Application startup complete.")
    
    except Exception as e:
        print("Exception occured",e)
        logger.error("Either Odoo or Supabase is not working")