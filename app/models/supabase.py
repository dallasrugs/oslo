from pydantic import BaseModel
from datetime import datetime 

'''
    Classes from Supabase Database Tables
'''

class Category(BaseModel):
    name: str 
    description: str  

class Items(BaseModel):
    title: str 
    description: str 
    altText: str
    path: str 
    categoryId: int 
