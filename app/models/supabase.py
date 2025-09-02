from pydantic import BaseModel
from datetime import datetime 
from typing import Optional 
'''
    Classes from Supabase Database Tables
'''

class Category(BaseModel):
    name: str 
    description: str  
    
class Subcategory(BaseModel):
    name: str 
    description: str 

class Items(BaseModel):
    title: str 
    description: str 
    category_id: int 

class ItemUpdate(BaseModel):
    title: str 
    description: str
    category_id: int
    url: Optional[str] = None 
