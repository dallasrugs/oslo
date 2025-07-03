
from fastapi import APIRouter, Depends, File, Form, UploadFile, Query, Response 
from fastapi.responses import JSONResponse
from routers.supabase import Supabase
from routers.odoo import Odoo 
from internal import status
from models.inquiry import Inquiry
import models.supabase as spb
from internal.logger import logger
from internal.templates import Messages
from internal.utilities import ImageUploader 
import os 
import json 

router = APIRouter()

## Supabase ROUTES
def get_Supabase_instance() -> Supabase:
    if status.supabase_instance is None:
        logger.error("Supabase instance not yet initialized")
    return status.supabase_instance

## Odoo Integration 
def get_odoo_instance() -> Odoo:
    if status.odoo_instance is None:
        logger.error("Odoo Instance is probably not running")
    return status.odoo_instance


# HOME 
@router.get("/")
async def home():
    return {"message": "Welcome to Oslo, not Norway. Please do not use this endpoint directly.", "server_status": {
        "Supabase Instance": "Operational" if get_Supabase_instance() is not None else "Server Error, Supabase Instance is not loaded. Check Console", 
        "Odoo Instance": "Operational" if get_odoo_instance() is not None else "Server Error, Odoo Instance is not loaded. Check Console" 
    }}

# GET REQUESTS
@router.get("/categories")
async def get_categories(
    filter: str = Query("{}", alias="filter"),
    range: str = Query("[0,24]", alias="range"),
    sort: str = Query('["id","DESC"]', alias="sort"),
    supabase: Supabase = Depends(get_Supabase_instance)
):
    try:
        categories = await supabase.categories(filter, range, sort)
        total = supabase.count_categories(filter)

    except Exception as e:
        return Messages.exception_message(
            origin="routers/routes.py",
            message="Issue in retrieving categories, please check exception",
            exception=e
        )

    range_list = json.loads(range)
    start, end = range_list
    content_range = f"categories {start}-{start + len(categories) - 1}/{total}"

    # Convert RowMapping to dict
    categories_dict = [dict(row) for row in categories]

    return Messages.message(
        content=categories_dict,
        headers={
            "Content-Range": content_range,
        }
    )


@router.get("/categories/{category_id}")
async def get_category_by_id(category_id: int, Supabase: Supabase = Depends(get_Supabase_instance)):
    return Supabase.getCategoryByID(category_id)

@router.get("/Product")
async def get_items(
    filter: str = Query("{}", alias="filter"),
    range: str = Query("[0,9]", alias="range"),
    sort: str = Query('["id","ASC"]', alias="sort"),
    supabase: Supabase = Depends(get_Supabase_instance)
):
    items = await supabase.items(filter, range, sort)
    total = supabase.count_items(filter)
    range_list = json.loads(range)
    start, end = range_list
    content_range = f"items {start}-{start + len(items) - 1}/{total}"

    # Convert RowMapping to dict
    items_dict = [dict(row) for row in items]

    return Response(
        content=json.dumps(items_dict, default=str),  
        media_type="application/json",
        headers={
            "Content-Range": content_range,
            "Access-Control-Expose-Headers": "Content-Range"  
        }
    )
@router.get("/Product/{item_id}")
async def get_items_by_id(item_id: int, supabase: Supabase = Depends(get_Supabase_instance)):
    item = supabase.getItembyID(item_id)
    item_dicts = [dict(row) for row in item]

    if not item_dicts:
        # Optional: return 404 if not found
        return Messages.user_error(message="Item Does Not Exist",status_code=404)

    return item_dicts[0]


# POST requests
@router.post("/categories/add")
async def add_category(category: spb.Category, supabase: Supabase = Depends(get_Supabase_instance)):
    return await supabase.addCategory(category.name,category.description)

@router.post("/products/add")
async def add_item(
    title: str = Form(...),
    description: str = Form(...),
    altText: str = Form(...),
    categoryId: int = Form(...),
    file: UploadFile = File(...),
    supabase: Supabase = Depends(get_Supabase_instance)
):
    # Save the uploaded file temporarily
    contents = await file.read()
    temp_file_path = f"uploads/{file.filename}"

    # Create a temporary directory to load images
    os.makedirs(os.path.dirname(temp_file_path), exist_ok=True)
    with open(temp_file_path, "wb") as f:
        f.write(contents)

    result = await supabase.addNewItem(
        title,
        description,
        temp_file_path,
        altText,
        categoryId
    )

    # Optional: Delete file after upload
    os.remove(temp_file_path)

    return result


@router.post("/upload-image")
async def upload_image(
    item_id: int = Form(...),
    file: UploadFile = File(...),
    supabase: Supabase = Depends(get_Supabase_instance)
):
    try:
        # Save uploaded file temporarily
        contents = await file.read()
        temp_file_path = f"uploads/{file.filename}"
        os.makedirs(os.path.dirname(temp_file_path), exist_ok=True)
        with open(temp_file_path, "wb") as f:
            f.write(contents)

        # Upload to Supabase bucket
        results = await supabase.UpdateItemImage(item_id,temp_file_path)

        # Remove temp file
        os.remove(temp_file_path)

        return results
    except Exception as e:
        logger.error(f"Exception has occured: {e}")



# PUT requests 
@router.put("/categories/update/{category_id}")
async def update_category(category_id: int, category: spb.Category, supabase: Supabase = Depends(get_Supabase_instance)):
    return supabase.updateCategory(category_id,category.name,category.description)

# DELETE requests
@router.delete("/categories/delete/{category_id}")
async def delete_category(category_id: int, supabase: Supabase = Depends(get_Supabase_instance)):
    return supabase.deleteCategory(category_id)

@router.delete("/Product/{item_id}")
async def delete_item(item_id: int, supabase: Supabase = Depends(get_Supabase_instance)):
    return await supabase.DeleteItembyID(item_id)

## Odoo Routes 
# for testing, keep this 
@router.get("/odoo/users")
async def getOdooUsers(odoo: Odoo = Depends(get_odoo_instance)):
    return odoo.getUsers()

# Route used in calling 
@router.post("/odoo/inquiry")
async def create_inquiry(inquiry: Inquiry, odoo: Odoo = Depends(get_odoo_instance)):
    if odoo is None:
        return JSONResponse(
            status_code=500,
            content={"message": "Inquiry could not be processed. Odoo connection is unavailable."}
        )

    try:
        response = odoo.addInquiry(inquiry.dict())
        return response

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "message": "Failed to send request to Odoo. The service may be down or unreachable.",
                "exception": str(e)
            }
        )


