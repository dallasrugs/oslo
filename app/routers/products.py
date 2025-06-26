# file: console-api/routers/products.py
import sqlalchemy as db
from fastapi import HTTPException
from internal import status as conn # load connection details from database status 


class Product:
    def __init__(self):
        try:
            self.engine, self.metadata,self.session = conn.db_engine, conn.db_metadata, conn.db_session
            '''
            Defining Tables here
            '''
            # Tables
            self.Category = self.metadata.tables['sourcingDB.Category']
            self.Items = self.metadata.tables['sourcingDB.Item']
            self.ItemCategory = self.metadata.tables['sourcingDB.ItemCategory']
            self.ItemImage = self.metadata.tables['sourcingDB.ItemImage']

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Initialization error: {str(e)}")
    
    def categories(self):
        try:
            stmt = db.select(self.Category)
            results = self.session.execute(stmt).mappings().all()
            return results
             
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Retrieval error: {str(e)}")
    
    def items(self):
        try:
            stmt = db.select(self.Items.c.title,self.Items.c.description, self.Category.c.name, self.ItemImage.c.url
                             ).where(
                (self.Items.c.id == self.ItemCategory.c.itemId) &
                (self.Category.c.id == self.ItemCategory.c.categoryId) & 
                (self.ItemImage.c.itemId == self.Items.c.id))
            results = self.session.execute(stmt).mappings().all()
            return results 

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Retrieval error: {str(e)}")
    
    def getItembyID(self, id):
        try:
            stmt = db.select(self.Items.c.title,self.Items.c.description, self.Category.c.name, self.ItemImage.c.url
                             ).where(
                (self.Items.c.id == self.ItemCategory.c.itemId) &
                (self.Category.c.id == self.ItemCategory.c.categoryId) & 
                (self.ItemImage.c.itemId == self.Items.c.id) & 
                (self.Items.c.id == id))
            results = self.session.execute(stmt).mappings().all()
            return results 

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Retrieval error: {str(e)}")
    
    def getCategoryByID(self, category_id):
        try:
            stmt = db.select(self.Category).where(self.Category.c.id == category_id)
            results = self.session.execute(stmt).mappings().all()
            return results

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Retrieval error: {str(e)}")
        
    
    '''
    Features: Individual Add, Bulk Add
    '''

    def addCategory(self):
        try:
            '''
            Adding new category by adding the last inserted ID 
            '''
            query = db.insert(self.Category).values()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

        
    

        


