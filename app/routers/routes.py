from fastapi import APIRouter, Depends
from routers.products import Product
from routers.odoo import Odoo 
from internal import status
from models.inquiry import Inquiry

router = APIRouter()

@router.get("/")
async def home():
    return {"message": "Welcome to GSBAN Console API, please do not use this endpoint directly."}

## PRODUCTS ROUTES
def get_product_instance() -> Product:
    if status.product_instance is None:
        raise RuntimeError(" Product instance not yet initialized")
    return status.product_instance


@router.get("/categories")
async def get_categories(product: Product = Depends(get_product_instance)):
    return product.categories()

@router.get("/categories/{category_id}")
async def get_category_by_id(category_id: int, product: Product = Depends(get_product_instance)):
    return product.getCategoryByID(category_id)

@router.get("/products")
async def get_products(product: Product = Depends(get_product_instance)):
    return product.items()

@router.get("/products/{item_id}")
async def get_product_by_id(item_id: int, product: Product = Depends(get_product_instance)):
    return product.getItembyID(item_id)


## Odoo Integration 

def get_odoo_instance() -> Odoo:
    if status.odoo_instance is None:
        raise Exception("Odoo Instance is probably not running")
    return status.odoo_instance

## ODOO Routes 
# for testing, keep this 
@router.get("/odoo/users")
async def getOdooUsers(odoo: Odoo = Depends(get_odoo_instance)):
    return odoo.getUsers()

# Jai Mata Di! Lets Rock!
@router.post("/odoo/inquiry")
async def create_inquiry(inquiry: Inquiry, odoo: Odoo = Depends(get_odoo_instance)):
    return odoo.addInquiry(inquiry.dict())



